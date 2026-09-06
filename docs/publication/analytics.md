# Public analytics policy

OpenFS uses Google Analytics 4 only on the production GitHub Pages host and only after an explicit opt-in.

## Collection boundary

- The public measurement ID is configured in `config/public-analytics.json`.
- The Google tag is not loaded on local previews, pull-request artifacts, or other hostnames.
- The Google tag is not loaded until the visitor selects **Allow analytics**.
- Only a sanitized `page_view` event is sent. Its location contains the origin and pathname, without the query string or fragment.
- Site-search terms, Feedback text, and custom interaction events are outside the collection boundary.
- Advertising storage, advertising user data, ad personalization, and Google Signals are disabled in the site code.

## Maintainer configuration

In the GA4 property, keep Enhanced Measurement features that can derive search terms or interaction events disabled. Review the GA4 data-retention setting and access controls periodically. Changing the measurement ID or collection boundary requires review of the public configuration, schema, implementation, tests, and privacy notice in the same Pull Request.

## Consent changes

The visitor's choice is stored locally under the key declared in `config/public-analytics.json`. The public privacy page provides a control to grant or withdraw consent. Withdrawing consent prevents subsequent analytics events from this site; it does not retroactively delete data already sent to GA4.
