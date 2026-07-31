# Contact form → info@geometrisk.com.au (Apps Script)

The About page contact form POSTs `FormData` to the shared Apps Script Web App
(the same `/exec` endpoint the other forms use) with:

| field     | example                          |
|-----------|----------------------------------|
| `type`    | `contact`                        |
| `to`      | `info@geometrisk.com.au`         |
| `name`    | the enquirer's name              |
| `email`   | the enquirer's email             |
| `message` | their message                    |
| `page`    | `/about.html`                    |
| `ts`      | ISO timestamp                    |

For the form to actually **email info@geometrisk.com.au**, add a `contact`
branch to the Apps Script's `doPost`, then **redeploy the Web App** (Manage
deployments → Edit → New version) so the same `/exec` URL serves the update.

```javascript
function doPost(e) {
  var p = (e && e.parameter) || {};
  var type = p.type || '';

  if (type === 'contact') return handleContact_(p);

  // ... your existing handlers: broker, line_lead, sample_report ...

  return json_({ ok: true });
}

function handleContact_(p) {
  var to = 'info@geometrisk.com.au';               // fixed recipient (don't trust client 'to')
  var name = String(p.name || '').trim();
  var email = String(p.email || '').trim();
  var message = String(p.message || '').trim();

  var subject = 'Website enquiry' + (name ? ' — ' + name : '');
  var body =
    'Name: '  + (name  || '—') + '\n' +
    'Email: ' + (email || '—') + '\n' +
    'Page: '  + (p.page || '—') + '\n' +
    'Time: '  + (p.ts   || new Date().toISOString()) + '\n\n' +
    (message || '(no message)');

  var options = {};
  if (email) options.replyTo = email;              // reply goes straight to the enquirer
  MailApp.sendEmail(to, subject, body, options);

  // Optional: also log every enquiry to a "Contact" sheet
  // var ss = SpreadsheetApp.getActive();
  // var sh = ss.getSheetByName('Contact') || ss.insertSheet('Contact');
  // sh.appendRow([new Date(), name, email, message, p.page || '']);

  return json_({ ok: true });
}

function json_(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}
```

Notes:
- `MailApp.sendEmail` sends **from** the Google account that owns the script, and
  `to` is `info@geometrisk.com.au`, so the enquiry is delivered into that inbox.
  `replyTo` is set to the enquirer so replying reaches them directly.
- The front end already fires the request with `no-cors`-style FormData (no custom
  headers), so no CORS config is needed on the script.
- Test from the live site only — don't submit real test data casually, it emails.
