// ============================================================================
//  BraveService.cs - Single-file Brave browser locker (WinForms, .NET Framework)
//  Compiles with the in-box csc.exe shipped on every Windows machine.
// ============================================================================

using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Drawing;
using System.Reflection;
using System.Runtime.InteropServices;
using System.Security.Cryptography;
using System.Text;
using System.Threading;
using System.Windows.Forms;
using Microsoft.Win32;

namespace BraveService
{
    // ------------------------------------------------------------------------
    internal static class NativeMethods
    {
        private const uint PROCESS_SUSPEND_RESUME = 0x0800;

        [DllImport("ntdll.dll")]
        private static extern uint NtSuspendProcess(IntPtr handle);

        [DllImport("ntdll.dll")]
        private static extern uint NtResumeProcess(IntPtr handle);

        [DllImport("kernel32.dll", SetLastError = true)]
        private static extern IntPtr OpenProcess(
            uint access,
            [MarshalAs(UnmanagedType.Bool)] bool inherit,
            int pid);

        [DllImport("kernel32.dll", SetLastError = true)]
        [return: MarshalAs(UnmanagedType.Bool)]
        private static extern bool CloseHandle(IntPtr h);

        public static bool Suspend(int pid)
        {
            IntPtr h = OpenProcess(PROCESS_SUSPEND_RESUME, false, pid);
            if (h == IntPtr.Zero) return false;
            try { return NtSuspendProcess(h) == 0; }
            finally { CloseHandle(h); }
        }

        public static bool Resume(int pid)
        {
            IntPtr h = OpenProcess(PROCESS_SUSPEND_RESUME, false, pid);
            if (h == IntPtr.Zero) return false;
            try { return NtResumeProcess(h) == 0; }
            finally { CloseHandle(h); }
        }
    }

    // ------------------------------------------------------------------------
    internal static class StartupHelper
    {
        private const string RunKey    = @"Software\Microsoft\Windows\CurrentVersion\Run";
        private const string ValueName = "BraveService";

        public static bool IsEnabled()
        {
            try
            {
                using (RegistryKey k = Registry.CurrentUser.OpenSubKey(RunKey, false))
                {
                    if (k == null) return false;
                    return k.GetValue(ValueName) != null;
                }
            }
            catch { return false; }
        }

        public static void Enable()
        {
            try
            {
                using (RegistryKey k = Registry.CurrentUser.OpenSubKey(RunKey, true))
                {
                    if (k != null)
                        k.SetValue(ValueName, "\"" + Application.ExecutablePath + "\"");
                }
            }
            catch { }
        }

        public static void Disable()
        {
            try
            {
                using (RegistryKey k = Registry.CurrentUser.OpenSubKey(RunKey, true))
                {
                    if (k != null) k.DeleteValue(ValueName, false);
                }
            }
            catch { }
        }
    }

    // ------------------------------------------------------------------------
    internal class AppLocker
    {
        private readonly string _procName;
        private readonly string _hash;

        public bool IsUnlocked    { get; set; }
        public int  FailedAttempts { get; set; }

        public AppLocker(string targetApp, string hash)
        {
            if (string.IsNullOrEmpty(targetApp))
                throw new ArgumentNullException("targetApp");

            string n = targetApp;
            if (n.EndsWith(".exe", StringComparison.OrdinalIgnoreCase))
                n = n.Substring(0, n.Length - 4);

            _procName = n;
            _hash     = hash;
        }

        public List<Process> GetTargets()
        {
            var list = new List<Process>();
            try
            {
                foreach (Process p in Process.GetProcessesByName(_procName))
                {
                    try { IntPtr h = p.Handle; list.Add(p); }
                    catch { try { p.Dispose(); } catch { } }
                }
            }
            catch { }
            return list;
        }

        public void SuspendAll(List<Process> procs)
        {
            foreach (Process p in procs)
            {
                try { NativeMethods.Suspend(p.Id); } catch { }
            }
        }

        public void ResumeAll(List<Process> procs)
        {
            foreach (Process p in procs)
            {
                try { NativeMethods.Resume(p.Id); } catch { }
            }
        }

        public void KillAll(List<Process> procs)
        {
            foreach (Process p in procs)
            {
                try { p.Kill(); } catch { }
                try { p.Dispose(); } catch { }
            }
        }

        public bool CheckPassword(string input)
        {
            if (string.IsNullOrEmpty(input)) return false;
            try
            {
                using (SHA256 sha = SHA256.Create())
                {
                    byte[] b = sha.ComputeHash(Encoding.UTF8.GetBytes(input));
                    StringBuilder sb = new StringBuilder(b.Length * 2);
                    foreach (byte x in b) sb.Append(x.ToString("x2"));
                    return string.Equals(sb.ToString(), _hash, StringComparison.OrdinalIgnoreCase);
                }
            }
            catch { return false; }
        }
    }

    // ------------------------------------------------------------------------
    internal class PasswordForm : Form
    {
        private TextBox _entry;
        private string  _password;
        private bool    _cancelled;

        public string Password  { get { return _password; } }
        public bool   Cancelled { get { return _cancelled; } }

        public PasswordForm(string subtitle, Icon icon)
        {
            _password  = "";
            _cancelled = true;

            SuspendLayout();

            Text            = "Brave";
            ClientSize      = new Size(380, 240);
            BackColor       = Color.FromArgb(0x20, 0x23, 0x24);
            FormBorderStyle = FormBorderStyle.FixedSingle;
            MaximizeBox     = false;
            MinimizeBox     = false;
            StartPosition   = FormStartPosition.CenterScreen;
            TopMost         = true;
            ShowIcon        = icon != null;
            if (icon != null) Icon = icon;

            Label title = new Label();
            title.Text      = "Brave Security Guard";
            title.Font      = new Font("Segoe UI", 18F, FontStyle.Bold);
            title.ForeColor = Color.FromArgb(0xFB, 0x54, 0x2B);
            title.BackColor = Color.Transparent;
            title.TextAlign = ContentAlignment.MiddleCenter;
            title.Location  = new Point(0, 20);
            title.Size      = new Size(378, 40);

            Label sub = new Label();
            sub.Text      = subtitle;
            sub.Font      = new Font("Segoe UI", 9.5F);
            sub.ForeColor = Color.FromArgb(0xE0, 0xE0, 0xE0);
            sub.BackColor = Color.Transparent;
            sub.TextAlign = ContentAlignment.MiddleCenter;
            sub.Location  = new Point(0, 62);
            sub.Size      = new Size(378, 20);

            Panel panel = new Panel();
            panel.BackColor = Color.FromArgb(0x30, 0x34, 0x36);
            panel.Location  = new Point(45, 92);
            panel.Size      = new Size(288, 42);

            _entry = new TextBox();
            _entry.Font         = new Font("Segoe UI", 16F);
            _entry.BackColor    = Color.FromArgb(0x30, 0x34, 0x36);
            _entry.ForeColor    = Color.White;
            _entry.BorderStyle  = BorderStyle.None;
            _entry.TextAlign    = HorizontalAlignment.Center;
            _entry.PasswordChar = '✵';
            _entry.Location     = new Point(0, 8);
            _entry.Width        = 288;
            _entry.MaxLength    = 256;
            panel.Controls.Add(_entry);

            Button btn = new Button();
            btn.Text      = "UNLOCK";
            btn.Font      = new Font("Segoe UI", 10F, FontStyle.Bold);
            btn.BackColor = Color.FromArgb(0xFB, 0x54, 0x2B);
            btn.ForeColor = Color.White;
            btn.FlatStyle = FlatStyle.Flat;
            btn.Location  = new Point(45, 150);
            btn.Size      = new Size(288, 38);
            btn.Cursor    = Cursors.Hand;
            btn.TabStop   = false;
            btn.FlatAppearance.BorderSize         = 0;
            btn.FlatAppearance.MouseOverBackColor = Color.FromArgb(0xE0, 0x41, 0x1B);
            btn.FlatAppearance.MouseDownBackColor = Color.FromArgb(0xE0, 0x41, 0x1B);
            btn.Click += new EventHandler(OnSubmit);

            Controls.Add(title);
            Controls.Add(sub);
            Controls.Add(panel);
            Controls.Add(btn);

            KeyPreview = true;
            KeyDown += new KeyEventHandler(OnFormKeyDown);
            Shown   += new EventHandler(OnFormShown);

            ResumeLayout(false);
        }

        private void OnFormShown(object sender, EventArgs e)
        {
            _entry.Focus();
            _entry.SelectAll();
        }

        private void OnFormKeyDown(object sender, KeyEventArgs e)
        {
            if (e.KeyCode == Keys.Enter) { e.SuppressKeyPress = true; Submit(); }
            else if (e.KeyCode == Keys.Escape) { e.SuppressKeyPress = true; Close(); }
        }

        private void OnSubmit(object sender, EventArgs e) { Submit(); }

        private void Submit()
        {
            _password  = _entry.Text ?? "";
            _cancelled = false;
            Close();
        }
    }

    // ------------------------------------------------------------------------
    internal class MainForm : Form
    {
        private const string TargetApp    = "brave.exe";
        private const string PasswordHash =
            "5ec1f7e700f37c3d0b2981d04855fc34b94aaa15457b05ca571817442d228f81";
        private const int MaxFails        = 3;
        private static readonly TimeSpan Lockout = TimeSpan.FromSeconds(30);
        private const int PollMs          = 300;

        private readonly IntPtr _handleForce;   // forces handle creation for Invoke()
        private NotifyIcon      _tray;
        private AppLocker       _locker;
        private Thread          _worker;
        private Icon            _appIcon;
        private bool            _ownsIcon;
        private volatile bool   _running;
        private DateTime        _lockoutUntil;

        public MainForm()
        {
            _running      = true;
            _lockoutUntil = DateTime.MinValue;

            ShowInTaskbar   = false;
            FormBorderStyle = FormBorderStyle.None;
            StartPosition   = FormStartPosition.Manual;
            Location        = new Point(-32000, -32000);
            Size            = new Size(1, 1);
            WindowState     = FormWindowState.Minimized;

            _appIcon = LoadAppIcon(out _ownsIcon);
            Icon     = _appIcon;

            _locker = new AppLocker(TargetApp, PasswordHash);

            // Force window handle so worker thread can call Invoke() safely
            _handleForce = Handle;

            // Recover anything left suspended by a previous crash
            try
            {
                List<Process> stale = _locker.GetTargets();
                _locker.ResumeAll(stale);
                _locker.ResumeAll(stale);
            }
            catch { }
        }

        protected override void OnLoad(EventArgs e)
        {
            base.OnLoad(e);
            BuildTray();
            StartWorker();
        }

        // --------------------------------------------------------------------
        private static Icon LoadAppIcon(out bool owned)
        {
            owned = false;

            // 1) Best quality: embedded original icon
            try
            {
                Assembly asm   = Assembly.GetExecutingAssembly();
                string prefix  = asm.GetName().Name + ".icon.ico";
                string[] names = new string[] { prefix, "BraveService.icon.ico" };
                foreach (string name in names)
                {
                    System.IO.Stream s = asm.GetManifestResourceStream(name);
                    if (s != null)
                    {
                        using (s)
                        {
                            Icon ic = new Icon(s);
                            owned = true;
                            return ic;
                        }
                    }
                }
            }
            catch { }

            // 2) Whatever icon is embedded in the exe
            try
            {
                Icon ic = Icon.ExtractAssociatedIcon(Application.ExecutablePath);
                if (ic != null) { owned = true; return ic; }
            }
            catch { }

            // 3) Fallback
            return SystemIcons.Shield;
        }

        // --------------------------------------------------------------------
        private void BuildTray()
        {
            _tray = new NotifyIcon();
            _tray.Icon    = _appIcon;
            _tray.Text    = "Brave Service - Protected";
            _tray.Visible = true;

            ContextMenuStrip menu = new ContextMenuStrip();

            ToolStripMenuItem status = new ToolStripMenuItem("Brave Service is running");
            status.Enabled = false;
            menu.Items.Add(status);
            menu.Items.Add(new ToolStripSeparator());

            ToolStripMenuItem startup = new ToolStripMenuItem("Run at Windows startup");
            startup.CheckOnClick = true;
            startup.Checked      = StartupHelper.IsEnabled();
            startup.CheckedChanged += new EventHandler(OnStartupToggled);
            menu.Items.Add(startup);

            menu.Items.Add(new ToolStripSeparator());
            menu.Items.Add("Quit...", null, new EventHandler(OnQuit));

            _tray.ContextMenuStrip = menu;
            _tray.DoubleClick += new EventHandler(OnTrayDoubleClick);
        }

        private void OnStartupToggled(object sender, EventArgs e)
        {
            ToolStripMenuItem mi = sender as ToolStripMenuItem;
            if (mi == null) return;
            if (mi.Checked) StartupHelper.Enable();
            else            StartupHelper.Disable();
        }

        private void OnTrayDoubleClick(object sender, EventArgs e)
        {
            if (_tray == null) return;
            string msg = _locker.IsUnlocked ? "Status: Unlocked" : "Status: Protected";
            _tray.ShowBalloonTip(2000, "Brave Service", msg, ToolTipIcon.Info);
        }

        // --------------------------------------------------------------------
        private void StartWorker()
        {
            if (_worker != null) return;
            _worker = new Thread(WorkerLoop);
            _worker.IsBackground = true;
            _worker.Name         = "BraveServiceWorker";
            _worker.Priority     = ThreadPriority.BelowNormal;
            _worker.Start();
        }

        private void WorkerLoop()
        {
            while (_running)
            {
                try { Tick(); } catch { }
                try { Thread.Sleep(PollMs); } catch { }
            }
        }

        private void Tick()
        {
            List<Process> procs = _locker.GetTargets();

            // Lockout window: silently kill, never prompt
            if (DateTime.UtcNow < _lockoutUntil)
            {
                if (procs.Count > 0) _locker.KillAll(procs);
                return;
            }

            if (procs.Count > 0 && !_locker.IsUnlocked)
            {
                _locker.SuspendAll(procs);

                string pwd = PromptForPassword("Authentication required to proceed:");
                if (_locker.CheckPassword(pwd))
                {
                    _locker.ResumeAll(procs);
                    _locker.IsUnlocked     = true;
                    _locker.FailedAttempts = 0;
                }
                else
                {
                    _locker.KillAll(procs);
                    _locker.FailedAttempts++;
                    if (_locker.FailedAttempts >= MaxFails)
                    {
                        _lockoutUntil          = DateTime.UtcNow + Lockout;
                        _locker.FailedAttempts = 0;
                    }
                }
            }
            else if (procs.Count == 0 && _locker.IsUnlocked)
            {
                _locker.IsUnlocked = false;
            }
        }

        private string PromptForPassword(string subtitle)
        {
            try
            {
                if (InvokeRequired)
                    return (string)Invoke(new Func<string, string>(PromptCore), subtitle);
                return PromptCore(subtitle);
            }
            catch (ObjectDisposedException)   { return ""; }
            catch (InvalidOperationException) { return ""; }
        }

        private string PromptCore(string subtitle)
        {
            using (PasswordForm f = new PasswordForm(subtitle, _appIcon))
            {
                f.ShowDialog(this);
                return f.Cancelled ? "" : f.Password;
            }
        }

        // --------------------------------------------------------------------
        private void OnQuit(object sender, EventArgs e)
        {
            string pwd = PromptForPassword("Enter password to quit Brave Service:");
            if (!_locker.CheckPassword(pwd)) return;

            _running = false;
            try
            {
                List<Process> procs = _locker.GetTargets();
                _locker.ResumeAll(procs);
            }
            catch { }

            if (_tray != null)
            {
                _tray.Visible = false;
                _tray.Dispose();
                _tray = null;
            }

            Close();
        }

        protected override void OnFormClosing(FormClosingEventArgs e)
        {
            _running = false;
            if (_tray != null)
            {
                try { _tray.Visible = false; _tray.Dispose(); } catch { }
                _tray = null;
            }
            if (_ownsIcon && _appIcon != null)
            {
                try { _appIcon.Dispose(); } catch { }
                _appIcon = null;
            }
            base.OnFormClosing(e);
        }

        // keep the compiler quiet about the field we deliberately keep alive
        private IntPtr HandleGuard { get { return _handleForce; } }
    }

    // ------------------------------------------------------------------------
    internal static class Program
    {
        private const string MutexName =
            @"Global\BraveService_SingleInstance_5A4B28C1-9E7D-4F3A-B1C2-D4E5F6A7B8C9";

        [STAThread]
        private static void Main()
        {
            bool createdNew;
            using (Mutex mtx = new Mutex(false, MutexName, out createdNew))
            {
                if (!createdNew)
                {
                    MessageBox.Show(
                        "Brave Service is already running.",
                        "Brave Service",
                        MessageBoxButtons.OK,
                        MessageBoxIcon.Information);
                    return;
                }

                Application.EnableVisualStyles();
                Application.SetCompatibleTextRenderingDefault(false);
                Application.Run(new MainForm());
            }
        }
    }
}