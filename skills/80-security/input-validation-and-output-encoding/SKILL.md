---
name: input-validation-and-output-encoding
description: Use when accepting external input or rendering data back to a user interface, to prevent injection and cross-site scripting through allow-listing and context-aware encoding.
category: security
tags: [validation, encoding, xss, injection]
maturity: stable
updated: 2026-08-21
---

## Purpose

Nearly all injection vulnerabilities (SQL injection, XSS, command injection) share a root cause: untrusted input is trusted as code or markup rather than data. This skill covers validating input at trust boundaries and encoding output for the context it's rendered into, as the layered defense against these classes of vulnerability.

It complements skills/80-security/secure-coding-owasp-top-10/SKILL.md's injection guidance with concrete validation and encoding techniques.

## When to use / When NOT to use

**Use this skill when:**

- You are accepting input from a user, external API, file upload, or any untrusted source.
- You are rendering user-supplied or externally-sourced data into HTML, a URL, a query, or a shell command.
- A code review needs a checklist for validation and encoding coverage.

**Do NOT use this skill when:**

- The data being handled is fully internal, never derived from user input, and never crosses a trust boundary.
- You need the broader injection-prevention context — see skills/80-security/secure-coding-owasp-top-10/SKILL.md.

## Prerequisites

- skills/80-security/secure-coding-owasp-top-10/SKILL.md for the broader injection-prevention context.
- Framework-provided encoding utilities for your rendering context (e.g. Razor's automatic HTML encoding, React's JSX encoding).

## Workflow

1. **Validate input with an allow-list, not a deny-list** - Define what valid input looks like (format, length, character set) and reject everything else, rather than trying to blocklist known-bad patterns.
2. **Validate on the server, even if the client also validates** - Client-side validation is a UX convenience only; the server must independently enforce all validation rules.
3. **Use parameterized queries for any data access, never string building** - This remains the primary defense against SQL/command injection, as covered in skills/80-security/secure-coding-owasp-top-10/SKILL.md.
4. **Encode output for the exact context it's rendered into** - HTML-encode for HTML body content, attribute-encode for HTML attributes, URL-encode for URL components — each context needs its own encoding.
5. **Prefer framework auto-encoding over manual encoding** - Use Razor's `@` syntax or React's JSX rendering, which auto-encode by default, rather than manually concatenating raw HTML strings.
6. **Sanitize rich text/HTML input with an allow-list sanitizer** - If users can submit formatted HTML (e.g. a rich text editor), pass it through a library like HtmlSanitizer with an explicit allowed-tag list.
7. **Set a Content-Security-Policy as defense in depth** - CSP limits the damage of an XSS payload that slips through encoding, by restricting what scripts can execute.
8. **Validate file uploads by content, not just extension** - Check the actual file signature/content type server-side, not just the client-supplied filename extension.

## Decision guide

| Situation | Recommended approach |
| --- | --- |
| Rendering user-supplied text into an HTML page | Rely on the templating engine's automatic HTML encoding (Razor `@`, React JSX); never build raw HTML strings by concatenation. |
| Accepting a user-supplied value that will be part of a URL | URL-encode the value using the framework's URL encoding utility, not manual string replacement. |
| A user needs to submit rich formatted text (e.g. a comment with bold/links) | Pass the input through an allow-list HTML sanitizer library before storage/rendering, never store raw untrusted HTML unsanitized. |
| Validating an email address or phone number field | Use a well-tested format validator/allow-list pattern, and treat validation failure as a rejection, not a silent truncation. |
| An uploaded file's purpose is to be an image | Verify the actual file content/magic bytes match an image format server-side, not just trust the extension or MIME type header. |

## Reference implementation

Allow-list validation with a model and framework auto-encoding in a Razor view:

```csharp
public class CreateCommentRequest
{
    [Required, StringLength(1000, MinimumLength = 1)]
    public string Body { get; set; } = string.Empty;

    [Required, RegularExpression(@"^[a-zA-Z0-9_-]{3,30}$")]
    public string AuthorHandle { get; set; } = string.Empty;
}

[HttpPost("/comments")]
public async Task<IActionResult> Create([FromBody] CreateCommentRequest request, CancellationToken ct)
{
    if (!ModelState.IsValid) return ValidationProblem(ModelState);

    // Body is stored as-is; encoding happens at render time (see Razor view below),
    // not here at write time - this keeps the stored data faithful to the original input.
    await _mediator.Send(new CreateCommentCommand(request.AuthorHandle, request.Body), ct);
    return Created();
}
```

- The regular expression on AuthorHandle is an allow-list of exactly the accepted character set and length, not a blocklist of forbidden characters.
- Encoding is deferred to render time so the underlying stored data is not lossy or double-encoded.

### Automatic HTML encoding in a Razor view versus a manual raw-HTML anti-pattern

Razor's @ syntax HTML-encodes by default; @Html.Raw bypasses that protection:

```html
<!-- Safe: Razor automatically HTML-encodes the interpolated value -->
<p>@comment.Body</p>

<!-- Dangerous: bypasses encoding entirely, only use for pre-sanitized trusted HTML -->
<p>@Html.Raw(comment.Body)</p>
```

## Checklist

- [ ] All external input is validated server-side using an allow-list, regardless of client-side validation.
- [ ] Output is encoded for the specific context it's rendered into (HTML body, attribute, URL, JS).
- [ ] Framework auto-encoding is used by default; raw/unescaped rendering is an explicit, reviewed exception.
- [ ] Rich text/HTML input is passed through an allow-list sanitizer before storage or rendering.
- [ ] A Content-Security-Policy is configured as defense in depth against any XSS that slips through.
- [ ] File uploads are validated by actual content/signature, not just filename extension or client MIME type.

## Anti-patterns

- **Deny-list validation** - Trying to blocklist known-bad characters or patterns instead of allow-listing what valid input looks like, which is easily bypassed.
- **Client-side-only validation** - Trusting JavaScript form validation as the only enforcement, allowing direct API calls to bypass it entirely.
- **Raw HTML concatenation** - Building HTML strings by concatenating user input directly instead of relying on framework auto-encoding.
- **Storing sanitized instead of encoding at render** - Sanitizing/encoding input at write time and storing the already-encoded value, causing double-encoding or loss of original data fidelity.
- **Trusting file extensions** - Accepting an uploaded file's type based solely on its filename extension or client-supplied Content-Type header.

## Verification

- A test submitting a script-tag payload as user input confirms it renders as inert encoded text, not executable script.
- A test submitting malformed input against a validated field confirms server-side rejection even when client-side validation is bypassed.
- A file upload test with a renamed file (wrong extension for its real content) is rejected server-side.
- A CSP header is present in HTTP responses and restricts script sources appropriately.

## References

- skills/80-security/secure-coding-owasp-top-10/SKILL.md
- OWASP Input Validation Cheat Sheet.
- OWASP Cross Site Scripting Prevention Cheat Sheet.
