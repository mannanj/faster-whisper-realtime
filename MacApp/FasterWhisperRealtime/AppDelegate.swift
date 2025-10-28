import Cocoa
import Foundation

class AppDelegate: NSObject, NSApplicationDelegate {
    var serverProcess: Process?
    var serverMonitorTimer: Timer?
    var isServerReady = false

    func applicationDidFinishLaunching(_ notification: Notification) {
        startPythonServer()
        monitorServerHealth()
    }

    func applicationWillTerminate(_ notification: Notification) {
        stopPythonServer()
    }

    func applicationShouldTerminateAfterLastWindowClosed(_ sender: NSApplication) -> Bool {
        return true
    }

    func startPythonServer() {
        guard let resourcePath = Bundle.main.resourcePath else {
            print("Error: Could not find resource path")
            return
        }

        let serverPath = (resourcePath as NSString).appendingPathComponent("server.py")

        serverProcess = Process()
        serverProcess?.executableURL = URL(fileURLWithPath: "/usr/bin/python3")
        serverProcess?.arguments = [serverPath]
        serverProcess?.currentDirectoryURL = URL(fileURLWithPath: resourcePath)

        let pipe = Pipe()
        serverProcess?.standardOutput = pipe
        serverProcess?.standardError = pipe

        do {
            try serverProcess?.run()
            print("Python server started successfully")
        } catch {
            print("Error starting Python server: \(error)")
        }
    }

    func stopPythonServer() {
        serverProcess?.terminate()
        serverProcess?.waitUntilExit()
        serverMonitorTimer?.invalidate()
        print("Python server stopped")
    }

    func monitorServerHealth() {
        serverMonitorTimer = Timer.scheduledTimer(withTimeInterval: 0.5, repeats: true) { [weak self] _ in
            guard let self = self else { return }

            if !self.isServerReady {
                self.checkServerHealth()
            } else {
                self.serverMonitorTimer?.invalidate()
            }
        }
    }

    func checkServerHealth() {
        guard let url = URL(string: "http://localhost:10000/") else { return }

        let task = URLSession.shared.dataTask(with: url) { [weak self] _, response, _ in
            if let httpResponse = response as? HTTPURLResponse, httpResponse.statusCode == 200 {
                DispatchQueue.main.async {
                    self?.isServerReady = true
                    print("Server is ready!")
                }
            }
        }
        task.resume()
    }
}
