import streamlit as st
import requests
import time

# ─────────────────────────────────────────────
#  Page config
# ─────────────────────────────────────────────
st.set_page_config(page_title="Network Speed Test", layout="wide")
st.title("🌐 Network Speed Test Tool")
st.markdown("**Real-Time Speed Test** | HTTP Latency · Packet Loss · Upload · Download")

# ─────────────────────────────────────────────
#  Server settings
# ─────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Server Settings")
    SERVER_URL = st.text_input(
        "Server URL",
        value="http://localhost:8000",
        help=(
            "Local:  http://localhost:8000\n"
            "Render: https://your-app.onrender.com"
        ),
    )
    NUM_PINGS        = st.slider("Ping Requests",    min_value=10,  max_value=100, value=30, step=5)
    UPLOAD_SIZE_MB   = st.slider("Upload Size (MB)", min_value=5,   max_value=50,  value=20, step=5)
    DOWNLOAD_SIZE_MB = st.slider("Download Size (MB)", min_value=5, max_value=50,  value=25, step=5)
    st.markdown("---")
    st.info(
        "**How it works (real speed test):**\n"
        "1. Deploy `server.py` on Render.\n"
        "2. Run this Streamlit app **locally**.\n"
        "3. Enter your Render URL above.\n"
        "👉 Now it measures YOUR actual internet speed to Render!"
    )
    st.caption("Run `uvicorn server:app` on the server machine first.")


# ─────────────────────────────────────────────
#  Latency + Packet Loss  (HTTP ping)
# ─────────────────────────────────────────────
def ping_test(server_url, num_pings):
    url  = f"{server_url.rstrip('/')}/ping"
    rtts = []
    sent = received = 0

    progress_bar = st.progress(0, text="Starting latency test…")
    status_text  = st.empty()

    for i in range(num_pings):
        try:
            t0  = time.perf_counter()
            r   = requests.get(url, timeout=2)
            rtt = (time.perf_counter() - t0) * 1000
            sent += 1
            if r.status_code == 200:
                rtts.append(rtt)
                received += 1
        except Exception:
            sent += 1

        pct  = (i + 1) / num_pings
        loss = ((sent - received) / sent * 100) if sent > 0 else 0
        progress_bar.progress(pct, text=f"Ping {i + 1} / {num_pings}")
        status_text.text(f"Sent: {sent}  |  Received: {received}  |  Loss so far: {loss:.1f}%")

    progress_bar.empty()
    status_text.empty()

    packet_loss  = ((sent - received) / sent * 100) if sent > 0 else 0
    avg_latency  = sum(rtts) / len(rtts) if rtts else 0
    min_latency  = min(rtts) if rtts else 0
    max_latency  = max(rtts) if rtts else 0
    jitter       = (max_latency - min_latency) if rtts else 0

    return {
        "packets_sent":     sent,
        "packets_received": received,
        "packet_loss":      round(packet_loss, 2),
        "latency_ms":       round(avg_latency, 2),
        "min_latency":      round(min_latency, 2),
        "max_latency":      round(max_latency, 2),
        "jitter_ms":        round(jitter, 2),
    }


# ─────────────────────────────────────────────
#  Upload Speed  (HTTP POST streaming)
# ─────────────────────────────────────────────
def upload_test(server_url, size_mb):
    url        = f"{server_url.rstrip('/')}/upload"
    target     = size_mb * 1024 * 1024
    CHUNK_SIZE = 65536
    CHUNK      = b"X" * CHUNK_SIZE

    bar        = st.progress(0, text="Preparing upload…")
    sent_total = 0
    start      = time.perf_counter()

    # Generator that also updates the progress bar
    def data_gen():
        nonlocal sent_total
        while sent_total < target:
            block       = min(CHUNK_SIZE, target - sent_total)
            sent_total += block
            yield CHUNK[:block]

    try:
        # Fire the upload — progress updates happen between yields
        with st.spinner(f"Uploading {size_mb} MB to server…"):
            r = requests.post(url, data=data_gen(), timeout=120)
        bar.empty()

        if r.status_code == 200:
            result = r.json()
            return result.get("speed_mbps", 0.0)
        else:
            st.error(f"Upload failed: HTTP {r.status_code}")
            return 0.0

    except Exception as e:
        bar.empty()
        st.error(f"Upload error: {e}")
        return 0.0


# ─────────────────────────────────────────────
#  Download Speed  (HTTP GET streaming)
# ─────────────────────────────────────────────
def download_test(server_url, size_mb):
    url    = f"{server_url.rstrip('/')}/download?size_mb={size_mb}"
    target = size_mb * 1024 * 1024

    bar            = st.progress(0, text="Downloading data…")
    total_received = 0
    start          = time.perf_counter()

    try:
        with requests.get(url, stream=True, timeout=120) as r:
            r.raise_for_status()
            for chunk in r.iter_content(chunk_size=65536):
                if chunk:
                    total_received += len(chunk)
                    pct = min(total_received / target, 1.0)
                    bar.progress(
                        pct,
                        text=f"Downloading… {total_received // 1024} KB / {target // 1024} KB",
                    )

        duration   = max(time.perf_counter() - start, 0.001)
        speed_mbps = (total_received * 8) / (duration * 1_000_000)
        bar.empty()
        return round(speed_mbps, 2)

    except Exception as e:
        bar.empty()
        st.error(f"Download error: {e}")
        return 0.0


# ─────────────────────────────────────────────
#  Connection check
# ─────────────────────────────────────────────
def check_connection(server_url):
    try:
        r = requests.get(f"{server_url.rstrip('/')}/ping", timeout=5)
        return r.status_code == 200
    except Exception:
        return False


# ─────────────────────────────────────────────
#  UI — Run button
# ─────────────────────────────────────────────
if st.button("🚀 Start Complete Network Test", type="primary", use_container_width=True):

    with st.spinner(f"Checking connection to {SERVER_URL}…"):
        reachable = check_connection(SERVER_URL)

    if not reachable:
        st.error(
            f"❌ Cannot reach **{SERVER_URL}**.\n\n"
            "Make sure:\n"
            "1. `server.py` is running (locally: `uvicorn server:app --port 8000`).\n"
            "2. For Render: paste your full `https://your-app.onrender.com` URL.\n"
            "3. The URL has no trailing slash issues."
        )
        st.stop()

    st.success(f"✅ Connected to {SERVER_URL}")
    st.divider()

    # ── Latency / Packet Loss ─────────────────
    st.subheader("📡 Step 1: Latency Test (HTTP Ping)")
    ping_results = ping_test(SERVER_URL, int(NUM_PINGS))

    # ── Upload ────────────────────────────────
    st.subheader("📤 Step 2: Upload Speed (HTTP POST)")
    upload_mbps = upload_test(SERVER_URL, int(UPLOAD_SIZE_MB))

    # ── Download ──────────────────────────────
    st.subheader("📥 Step 3: Download Speed (HTTP GET)")
    download_mbps = download_test(SERVER_URL, int(DOWNLOAD_SIZE_MB))

    # ── Summary ───────────────────────────────
    st.divider()
    st.subheader("📊 Results Summary")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("⬇️ Download", f"{download_mbps:.2f} Mbps")
    c2.metric("⬆️ Upload",   f"{upload_mbps:.2f} Mbps")
    c3.metric("📶 Latency",  f"{ping_results['latency_ms']} ms")
    c4.metric(
        "📦 Packet Loss",
        f"{ping_results['packet_loss']}%",
        delta="High ⚠️" if ping_results['packet_loss'] > 5 else "Normal ✅",
        delta_color="inverse",
    )

    st.divider()
    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("**🔵 Latency Details**")
        st.write(f"- Requests Sent:    **{ping_results['packets_sent']}**")
        st.write(f"- Responses OK:     **{ping_results['packets_received']}**")
        st.write(f"- Avg Latency:      **{ping_results['latency_ms']} ms**")
        st.write(f"- Min Latency:      **{ping_results['min_latency']} ms**")
        st.write(f"- Max Latency:      **{ping_results['max_latency']} ms**")
        st.write(f"- Jitter:           **{ping_results['jitter_ms']} ms**")

    with col_b:
        st.markdown("**🟢 Speed Test Details**")
        st.write(f"- Upload Data:    **{UPLOAD_SIZE_MB} MB**")
        st.write(f"- Download Data:  **{DOWNLOAD_SIZE_MB} MB**")
        st.write(f"- Upload Speed:   **{upload_mbps:.2f} Mbps**")
        st.write(f"- Download Speed: **{download_mbps:.2f} Mbps**")
        st.write("- Transport: HTTP (works through all firewalls & proxies)")
        st.write(f"- Measured: YOUR machine → {SERVER_URL}")

    # ── Warnings ──────────────────────────────
    if ping_results['packet_loss'] > 20:
        st.warning("⚠️ Very high packet loss (> 20%). Network path is unstable.")
    elif ping_results['packet_loss'] > 5:
        st.warning("⚠️ Moderate packet loss detected. Check network stability.")

    if ping_results['latency_ms'] > 150:
        st.warning("⚠️ High latency (> 150 ms). Long distance or congestion detected.")

    if ping_results['jitter_ms'] > 50:
        st.warning("⚠️ High jitter. Real-time apps (VoIP, gaming) will be affected.")

st.caption("Real Computer Networks Mini Project | FastAPI Server + HTTP-based Streamlit Client")