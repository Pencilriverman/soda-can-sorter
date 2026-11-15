using System;
using System.Diagnostics;
using System.IO;
using System.Net;
using System.Net.Sockets;
using System.Security.Cryptography;
using System.Text;
using System.Threading;
using System.Windows.Forms;

static class Launcher
{
    static readonly string Root = AppDomain.CurrentDomain.BaseDirectory;
    static readonly string State = Path.Combine(Root, "runtime", "studio.port");

    static WebClient Client()
    {
        return new WebClient { Proxy = null };
    }

    static string Endpoint(int port)
    {
        return "http://127.0.0.1:" + port;
    }

    static int ExistingPort()
    {
        int port;
        if (!File.Exists(State) || !int.TryParse(File.ReadAllText(State), out port))
            throw new InvalidOperationException("Studio is not running or is still starting.");
        return port;
    }

    static string Session(int port)
    {
        using (var client = Client())
        {
            string response = client.DownloadString(Endpoint(port) + "/api/session");
            return response.Split('"')[3];
        }
    }

    [STAThread]
    static int Main(string[] args)
    {
        bool quiet = Array.IndexOf(args, "--no-browser") >= 0;
        try
        {
            string key;
            using (var sha = SHA256.Create())
                key = Convert.ToBase64String(sha.ComputeHash(Encoding.UTF8.GetBytes(Root.ToUpperInvariant()))).Replace("/", "_");
            using (var mutex = new Mutex(false, @"Local\GTA-AutoClip-" + key))
            {
                bool owns;
                try { owns = mutex.WaitOne(0); }
                catch (AbandonedMutexException) { owns = true; }
                if (Array.IndexOf(args, "--stop") >= 0)
                {
                    if (owns) { mutex.ReleaseMutex(); return 0; }
                    int port = ExistingPort();
                    using (var client = Client())
                    {
                        client.Headers["X-Studio-Token"] = Session(port);
                        client.UploadString(Endpoint(port) + "/api/stop", "{}");
                    }
                    return 0;
                }
                if (!owns)
                {
                    if (!quiet) Process.Start(Endpoint(ExistingPort()));
                    return 0;
                }
                try { Start(quiet); }
                finally { mutex.ReleaseMutex(); }
            }
            return 0;
        }
        catch (Exception error)
        {
            try { File.WriteAllText(Path.Combine(Root, "startup-error.log"), error.ToString()); }
            catch (IOException) { }
            if (!quiet) MessageBox.Show(error.Message, "GTA AutoClip Studio", MessageBoxButtons.OK, MessageBoxIcon.Error);
            return 1;
        }
    }

    static void Start(bool quiet)
    {
        File.Delete(State);
        foreach (string relative in new[] {
            "runtime/python/python.exe", "runtime/ffmpeg/ffmpeg.exe", "runtime/ffmpeg/ffprobe.exe",
            "runtime/yt-dlp/yt-dlp.exe", "runtime/backend/studio.py",
            "config/settings.json", "config/models.json", "frontend/dist/index.html" })
            if (!File.Exists(Path.Combine(Root, relative)))
                throw new FileNotFoundException("Missing bundled component " + relative);
        const int port = 57286;
        var info = new ProcessStartInfo
        {
            FileName = Path.Combine(Root, "runtime", "python", "python.exe"),
            Arguments = "-I -B -u runtime/backend/studio.py --bind 0.0.0.0 --port " + port,
            WorkingDirectory = Root,
            UseShellExecute = false,
            CreateNoWindow = true,
            RedirectStandardError = true
        };
        string log = Path.Combine(Root, "launcher.log");
        using (var child = new Process { StartInfo = info })
        {
            child.ErrorDataReceived += (sender, line) =>
            {
                if (line.Data != null)
                    try { File.AppendAllText(log, line.Data + Environment.NewLine); }
                    catch (IOException) { }
            };
            child.Start();
            child.BeginErrorReadLine();
            try
            {
                bool ready = false;
                for (int attempt = 0; attempt < 100 && !child.HasExited; attempt++)
                {
                    try { Session(port); ready = true; break; }
                    catch (WebException) { Thread.Sleep(150); }
                }
                if (!ready) throw new InvalidOperationException("Studio did not start. See " + log);
                File.WriteAllText(State, port.ToString());
                if (!quiet)
                {
                    try { Process.Start(Endpoint(port)); }
                    catch (System.ComponentModel.Win32Exception)
                    {
                        MessageBox.Show("Open " + Endpoint(port) + " in your browser.", "GTA AutoClip Studio");
                    }
                }
                child.WaitForExit();
                if (child.ExitCode != 0)
                    throw new InvalidOperationException("Studio exited unexpectedly. See " + log);
            }
            finally
            {
                if (!child.HasExited) child.Kill();
                File.Delete(State);
            }
        }
    }
}
