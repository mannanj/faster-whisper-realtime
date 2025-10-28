# Optimization Guide: faster-whisper & CTranslate2

## What is CTranslate2?

**CTranslate2** is a specialized C++ and Python inference runtime for Transformer models, providing significant performance improvements over general-purpose frameworks like PyTorch or TensorFlow.

### Key Characteristics:
- **Purpose-built for inference**: Optimized specifically for deploying trained models, not training
- **Cross-platform**: Supports x86-64, ARM64, CPU, and GPU (NVIDIA CUDA, Apple Metal)
- **Lightweight**: Minimal dependencies, production-ready with backward compatibility
- **Model format**: Requires models converted to CTranslate2 format (faster-whisper handles this automatically)

### How It Works:
CTranslate2 applies multiple optimization techniques:
- **Quantization**: Reduce model precision (FP32 → FP16/INT8/INT4) for 4x smaller size
- **Layer fusion**: Combine operations to reduce memory transfers
- **Batch reordering**: Optimize GPU/CPU utilization
- **Dynamic memory**: Allocate only what's needed per request
- **Hardware-specific code paths**: Auto-detects CPU features (AVX2, AVX512) and dispatches optimized code

### Performance Example:
For Whisper transcription on CPU (4 threads):
- **CTranslate2 (faster-whisper)**: ~860 tokens/sec, 529MB memory
- **PyTorch (original Whisper)**: ~200-300 tokens/sec, 2-3GB memory

**Result**: ~3-4x faster with 75% less memory usage

---

## Why faster-whisper Uses CTranslate2

The `faster-whisper` library is essentially a wrapper around OpenAI's Whisper model converted to CTranslate2 format. This is why:
1. It cannot run in browsers (requires CTranslate2 C++ runtime)
2. It's significantly faster than `openai-whisper` package
3. It requires Python/server-side deployment

---

## Optimization Opportunities for This Project

### Current Configuration (server.py:15)
```python
model = WhisperModel("base", device="cpu", compute_type="int8")
```

**Status**: Already using INT8 quantization (good first step)

---

### Recommended Optimizations (Priority Order)

#### 1. Enable VAD (Voice Activity Detection) ⭐ HIGH IMPACT
**Current**: Not enabled
**Change**: Add `vad_filter=True` parameter

```python
segments, info = model.transcribe(
    temp_path,
    beam_size=5,
    vad_filter=True  # ADD THIS
)
```

**Benefits**:
- Automatically skips silent segments
- Reduces processing time by 30-50% for speech with pauses
- Lower CPU usage and faster response times
- No accuracy loss for actual speech

**Trade-off**: Adds ~10ms overhead for VAD computation (negligible)

---

#### 2. Reduce Beam Size ⭐ QUICK WIN
**Current**: `beam_size=5`
**Change**: Reduce to `beam_size=1` for real-time applications

```python
segments, info = model.transcribe(
    temp_path,
    beam_size=1,  # CHANGE FROM 5
    vad_filter=True
)
```

**Benefits**:
- 2-3x faster transcription
- Lower latency for real-time chunks
- Minimal accuracy loss for conversational speech

**Trade-off**: Slightly less accurate for complex/technical language

---

#### 3. Enable Batched Processing ⭐ HIGH IMPACT (Multiple Users)
**Current**: Sequential chunk processing
**Change**: Use `BatchedInferencePipeline` for concurrent requests

```python
from faster_whisper import BatchedInferencePipeline

model = WhisperModel("base", device="cpu", compute_type="int8")
batched_model = BatchedInferencePipeline(model=model)

# Use batched_model.transcribe() instead
```

**Benefits**:
- 60% faster when processing multiple chunks/users simultaneously
- Better server throughput
- Automatic batching of concurrent requests

**Benchmark** (from faster-whisper docs):
- Sequential: 2m37s for 5 audio files
- Batched (batch_size=8): 1m06s (2.4x speedup)

**Trade-off**: Slightly higher memory usage, added complexity

---

#### 4. GPU Acceleration 🚀 HIGHEST PERFORMANCE
**Current**: CPU-only processing
**Change**: Use CUDA GPU if available

```python
model = WhisperModel(
    "base",
    device="cuda",  # CHANGE FROM "cpu"
    compute_type="float16"  # CHANGE FROM "int8"
)
```

**Benefits**:
- 5-10x faster transcription
- Can handle larger models (small, medium) in real-time
- Lower CPU usage

**Requirements**:
- NVIDIA GPU with CUDA support
- CUDA 12 and cuDNN 9 installed
- ~2GB VRAM for base model

**Trade-off**: Requires GPU hardware, higher power consumption

---

#### 5. Optimize CPU Thread Count
**Current**: Default thread allocation
**Change**: Set optimal thread count for your CPU

```bash
# Before starting server
export OMP_NUM_THREADS=4  # Set to your CPU core count
python3 server.py
```

**Benefits**:
- Better CPU utilization
- Prevents thread thrashing on multi-core systems
- 10-20% performance improvement

**How to find your core count**:
```bash
# macOS
sysctl -n hw.ncpu

# Linux
nproc
```

---

#### 6. Consider Distil Models
**Current**: `base` model (74M parameters)
**Change**: Try `distil-large-v3` for better speed/accuracy ratio

```python
model = WhisperModel("distil-large-v3", device="cpu", compute_type="int8")
```

**Benefits**:
- Better accuracy than base model
- Faster than large-v3 (optimized architecture)
- Good for quality-sensitive applications

**Trade-off**:
- Larger model size (~1.5GB vs 150MB)
- Slower than tiny/base but faster than large-v3

---

#### 7. Word-Level Timestamps (Optional Enhancement)
**Current**: Segment-level timestamps only
**Change**: Enable word-level granularity

```python
segments, info = model.transcribe(
    temp_path,
    beam_size=1,
    vad_filter=True,
    word_timestamps=True  # ADD THIS
)

# Access via segment.words
for segment in segments:
    for word in segment.words:
        print(f"{word.word} [{word.start}s - {word.end}s]")
```

**Benefits**:
- Precise timing for each word
- Enables advanced UI features (highlight current word)
- Minimal performance penalty (<5%)

---

## Model Size Comparison

| Model | Parameters | Disk Size (INT8) | Speed | Quality |
|-------|-----------|------------------|-------|---------|
| tiny | 39M | ~75MB | Fastest | Basic |
| base | 74M | ~150MB | Fast | Good |
| small | 244M | ~500MB | Medium | Better |
| distil-large-v3 | 756M | ~1.5GB | Medium | Best |
| large-v3 | 1550M | ~3GB | Slow | Best |

**Current project uses**: `base` (good balance for CPU)

---

## Implementation Recommendations

### For Immediate Improvement (No Hardware Changes):
1. Enable VAD: `vad_filter=True`
2. Reduce beam size: `beam_size=1`
3. Set CPU threads: `export OMP_NUM_THREADS=<your_cores>`

**Expected Result**: 2-3x faster transcription with minimal code changes

### For Production Deployment:
1. All immediate improvements above
2. Implement `BatchedInferencePipeline` for concurrent users
3. Consider GPU if serving multiple users simultaneously

### For Best Quality:
1. Keep `beam_size=5`
2. Use `distil-large-v3` model
3. Enable `word_timestamps=True`
4. GPU recommended for real-time performance

---

## Why This Cannot Run in Browser

### Technical Limitations:
1. **No CTranslate2 JavaScript/WASM runtime**: CTranslate2 is C++ only, not compiled to WebAssembly
2. **Model size**: Even tiny model is ~75MB (large download for browsers)
3. **Compute requirements**: Real-time transcription needs significant CPU/GPU power
4. **No browser GPU APIs**: WebGPU exists but CTranslate2 isn't compatible

### Alternative: Browser-Based Transcription
If you need fully client-side transcription:
- **Whisper.cpp**: WASM-compiled version of Whisper (slower than CTranslate2)
- **WebSpeech API**: Browser native (limited language support, less accurate)
- **transformers.js**: Hugging Face models in browser (experimental, limited Whisper support)

**Trade-off**: All browser-based solutions are 5-10x slower than server-side faster-whisper

---

## Performance Monitoring

### Add Timing Metrics:
```python
import time

def transcribe_live():
    start_time = time.time()

    # ... existing code ...

    segments, info = model.transcribe(temp_path, beam_size=1, vad_filter=True)

    transcription_time = time.time() - start_time
    print(f"Transcription took {transcription_time:.2f}s for {info.duration:.2f}s audio")
    print(f"Real-time factor: {transcription_time / info.duration:.2f}x")
```

**Target for real-time**: RTF (Real-Time Factor) < 0.3 (transcription 3x faster than audio duration)

---

## References

- [faster-whisper GitHub](https://github.com/SYSTRAN/faster-whisper)
- [CTranslate2 Documentation](https://github.com/OpenNMT/CTranslate2)
- [Whisper Model Card](https://github.com/openai/whisper)
