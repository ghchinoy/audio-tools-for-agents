# Audio Tools Error Catalog & Remediation

When executing commands with `--json`, error responses include machine-readable error codes. Use this table for autonomous error handling.

| Error Code | Root Cause | Automated Agent Remediation |
| :--- | :--- | :--- |
| `ERR_LOW_MEMORY` | Available system RAM is below the safety threshold ($< 2.5\text{GB}$). | 1. Advise user of host memory pressure.<br>2. Switch from 6-stem to 4-stem model.<br>3. Close background processes or retry on larger worker instance. |
| `ERR_FILE_NOT_FOUND` | Specified audio input path does not exist on disk or cloud URI is unresolvable. | 1. Check path string for typos or shell escaping issues.<br>2. Run `ls` or file search tool to locate the audio file.<br>3. Verify cloud URI permissions if using `gs://`. |
| `ERR_INFERENCE_FAILED` | PyTorch runtime failure (e.g., corrupt audio header, CUDA device out of memory). | 1. Run `audio-tools inspect <path>` to check audio validity.<br>2. If `--device auto` was used, re-run with explicit `--device cpu`.<br>3. Check if audio is uncompressed PCM WAV; convert with `ffmpeg` if needed. |
| `ERR_UNSUPPORTED_SCHEME` | Cloud URI scheme is not supported (only `gs://` supported for cloud IO). | 1. Download file to local filesystem first using standard CLI tools (`curl`, `aws s3 cp`).<br>2. Pass resolved local filepath to `audio-tools`. |
