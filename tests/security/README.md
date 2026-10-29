# Authorized local security/privacy validation

Use only your own disposable local/staging HostelSpace instance with permission and fictional records. No external target probing or production-data testing is required by this pack.

The implemented backend tests cover anonymous/wrong-role/cross-student/other-warden access, strict protected fields, CSRF for session writes and login, nonfinite/invalid inputs, server snapshots and no student-sample model fields. The pending browser privacy test covers no location call before explicit click, denied-location no-write, no localStorage sample storage and hidden unauthorized workflow controls. Backend scopes, not those UI checks, enforce access.

Still required: real PostgreSQL concurrent acceptance/finalization tests; complete all-module owner/role checks; production login rate limits/session policy; reverse-proxy/APM/body-log inspection and retention review; HTTPS/cookie/CSRF host validation; third-party dependency/security review; payment credential-retention tests owned by Atiksh. Sample privacy is not proven just by observing one UI page or searching one model.

Do not enable browser traces/network-body exports for tests that use real location or credentials. Use only fictional samples. Never store credentials or location samples in Git, browser storage, traces, screenshots or shared logs.
