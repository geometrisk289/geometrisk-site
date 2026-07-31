# Advisor directory backend (Apps Script)

Two halves, both on the **same** `/exec` Web App you already use:

1. **Onboarding submit** — `broker-onboarding.html` POSTs `type=advisor_profile` → a row is
   appended to an **"Advisors"** sheet with `status = pending`.
2. **Finder read** — `find-advisor.html` loads live advisors via **JSONP**
   (`GET …/exec?type=advisors&callback=…`). JSONP is used because a plain `fetch` GET to
   `script.google.com` is blocked by CORS; a `<script>` tag isn't.

You review each row and change `status` to **live** for it to appear in the finder.

---

## 1. Add to `doPost`

Near the top of your existing `doPost(e)`, add:

```javascript
if (e && e.parameter && e.parameter.type === 'advisor_profile') return handleAdvisorProfile_(e.parameter);
```

Then paste this function at the bottom of the file:

```javascript
function handleAdvisorProfile_(p) {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sh = ss.getSheetByName('Advisors');
  if (!sh) {
    sh = ss.insertSheet('Advisors');
    sh.appendRow(['id','name','firm','role','afsl','email','phone','blurb',
                  'suburb','postcode','states','industries','bookingUrl',
                  'remuneration','status','timestamp']);
  }
  var id = String(p.firm || 'advisor').toLowerCase()
             .replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '')
           + '-' + Date.now().toString(36);
  sh.appendRow([
    id, p.name || '', p.firm || '', p.role || 'Risk Advisor', p.afsl || '',
    p.email || '', p.phone || '', p.blurb || '', p.suburb || '', p.postcode || '',
    p.states || '[]', p.industries || '[]', p.bookingUrl || '',
    p.remuneration || '{}', 'pending', new Date()
  ]);
  try {
    MailApp.sendEmail('info@geometrisk.com.au',
      'New advisor profile: ' + (p.firm || ''),
      'A new advisor profile is pending review.\n\n' +
      (p.name || '') + ' — ' + (p.firm || '') + '\n' + (p.email || '') +
      '\n\nSet its status to "live" in the Advisors sheet to publish it.');
  } catch (err) {}
  return json_({ ok: true });
}
```

## 2. Add a `doGet` (if you don't have one)

```javascript
function doGet(e) {
  var p = (e && e.parameter) || {};
  if (p.type === 'advisors') return advisorsFeed_(p.callback);
  return ContentService.createTextOutput('OK');
}

function advisorsFeed_(callback) {
  var out = [];
  var sh = SpreadsheetApp.getActiveSpreadsheet().getSheetByName('Advisors');
  if (sh) {
    var rows = sh.getDataRange().getValues();
    var head = rows.shift(), col = {};
    head.forEach(function (h, i) { col[h] = i; });
    rows.forEach(function (r) {
      if (String(r[col.status]).toLowerCase() !== 'live') return;
      var states = parseJson_(r[col.states], []);
      out.push({
        id: r[col.id], name: r[col.name], firm: r[col.firm],
        role: r[col.role] || 'Risk Advisor', afsl: r[col.afsl], photo: '',
        blurb: r[col.blurb],
        industries: parseJson_(r[col.industries], []),
        suburb: r[col.suburb], state: states[0] || '', states: states,
        bookingUrl: r[col.bookingUrl],
        remuneration: parseJson_(r[col.remuneration], {}),
        status: 'live'
      });
    });
  }
  var body = JSON.stringify(out);
  if (callback) {
    return ContentService.createTextOutput(callback + '(' + body + ')')
      .setMimeType(ContentService.MimeType.JAVASCRIPT);   // JSONP
  }
  return ContentService.createTextOutput(body)
    .setMimeType(ContentService.MimeType.JSON);
}

function parseJson_(v, dflt) { try { return JSON.parse(v); } catch (e) { return dflt; } }
```

> If you already have a `doGet`, just add the `if (p.type === 'advisors') …` line into it and paste `advisorsFeed_` + `parseJson_`.

## 3. Redeploy

**Deploy → Manage deployments → the "geometrisk website" deployment → ✏️ Edit → Version: New version → Deploy.** Same `/exec` URL, so no site change needed. Authorise if prompted (the GET reads the sheet; the POST sends the notification email).

## 4. Go-live workflow

- A broker submits at `broker-onboarding.html` → new **pending** row + you get an email.
- Review the row; when happy, set its **status** cell to `live`.
- It appears in the finder on the next load. Until any row is `live`, the finder shows the
  bundled seed advisors (`data/advisors.json`) so it's never empty.

## Field notes / TODO
- **Headshot/logo** isn't submitted yet (base64 data URLs exceed a sheet cell's ~50k limit).
  Later: upload to Drive and store the file URL in a `photo` column.
- **Distance/geocoding** and **meeting-type filter** are still TODO on the finder.
