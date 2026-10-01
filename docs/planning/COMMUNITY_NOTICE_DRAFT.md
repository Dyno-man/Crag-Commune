# Draft community and privacy notice

**Review draft — do not publish as a live site notice yet.** Discussion, reporting, deletion, backup, and recovery features described below do not all exist. Issue #28 tracks the decisions and implementation checks needed before discussion opens.

## Proposed member-facing text

### Who can join

Crag Commune is a small climbing community for people **13 or older**. Before account creation, we will ask members to confirm they meet that minimum age. We do not need a birth date for this check, and we do not verify government identity or climbing skill. Your public name may be a pseudonym. Do not post someone else's personal information or sensitive access locations.

### What other people can see

Your public name, profile bio, approximate home region, and public discussion posts and replies can be read by visitors. Outing titles, descriptions, dates, and host names are public. Accepted participants and the host can see the current private meetup details and participant list while an outing is open. A member notified of a change can see that change's history, including any meetup detail that changed while they were accepted. Cancellation notes go only to the host and members accepted at cancellation. People can copy or screenshot what they can view, so avoid putting a home address or other information you cannot take back into a post.

Your email address, if you provide one, is not shown on your profile. Passwords are stored using Django's password hashing. The service also stores account, participation, outing, notice, and authentication-limit records needed to operate the community. The limit records use keyed digests of submitted names or client addresses; they are not a public member directory. Do not put private health details into your profile or posts.

### Your content

You keep ownership of original writing and photos you contribute. You give Crag Commune permission to store, display, and moderate that content as needed to run the community. Posting does not put your content under the repository's MIT license or the catalog's proposed CC0 terms. Do not copy guidebook text, proprietary maps, other people's photos, or private correspondence. Public factual climbing corrections require a separate review and source record before they change the catalog or a planner result.

### Community care

The site owner is the initial moderator. Members can report spam, harassment, discriminatory conduct, impersonation, exposed personal details, and sensitive access information. The moderator may hide content or suspend an account and keep an internal record of the action. A member report about a closure or access restriction is a prompt for review, not an official reopening or closure announcement. For urgent access concerns, the owner will check current land-manager or SCC information and avoid reposting sensitive details. Crag Commune does not speak for those organizations.

### Requests and removal

Members can ask the owner to review or remove their content or account. Removing content from the live site cannot remove copies already downloaded or shared by other people. Some records may need to remain temporarily for moderation, security, or backup restoration; the exact periods and request channel must be published before this notice goes live. The site does not currently offer self-service account deletion or password recovery.

### How data is used

Member posts, profiles, private outing details, and email addresses are not part of public climbing-data exports and are not sent to a model provider as planner context. Community observations are personal reports, not verified route, trail, or access facts. The production host, backup location, and any email provider will be listed before public launch. Changes to this notice will be dated and shown to members before they materially change how content is used.

## Owner decisions and release checks

| Decision or check | Current proposal / status |
| --- | --- |
| Minimum age | Owner selected 13+. Add a required age-eligibility attestation at signup without collecting a birth date. Existing pilot accounts need a transition prompt. |
| Contact and report channel | Not configured. Add a private channel before discussion opens. |
| Reports and moderation | Not implemented. Report, hide, suspend, and audit actions are required before public posting. Owner is the sole initial moderator per the pilot decision. |
| Account deletion | Not implemented. Define request handling, live-record deletion or pseudonymization, and any retained audit fields. |
| Backup destination and expiry | Not selected. Owner asked to keep this notice in draft until backup retention is set and restore is tested. |
| Moderation audit retention | Not selected. Pick a bounded period and review access before publishing. |
| Outbound email and recovery | Not implemented. Email stays optional in the local pilot; see #27. |
| Post and reply terms | Confirm the display/moderation permission above and add explicit assent at posting before collecting member content. |
| Published notice | Blocked until the owner reviews this text, pending periods are set, and the described controls are tested. |

The [FTC's COPPA overview](https://www.ftc.gov/legal-library/browse/rules/childrens-online-privacy-protection-rule-coppa) describes rules involving personal information from children under 13. The chosen 13+ boundary is a product decision, and this draft is not legal advice.
