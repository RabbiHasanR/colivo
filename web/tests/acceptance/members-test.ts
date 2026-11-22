import { module, test } from 'qunit';
import { click, currentURL, fillIn, visit } from '@ember/test-helpers';
import { http, HttpResponse } from 'msw';
import { setupApplicationTest } from 'colivo-web/tests/helpers';
import { setupMsw, worker } from 'colivo-web/tests/helpers/msw';
import { loggedInAs, newHomeSetup } from 'colivo-web/tests/helpers/accounts';
import { member, membersApi, owner } from 'colivo-web/tests/helpers/members';

module('Acceptance | members', function (hooks) {
  setupApplicationTest(hooks);
  setupMsw(hooks, newHomeSetup);

  test('owner adds a member', async function (assert) {
    // GIVEN the owner of "Our Flat" is logged in; only they are a member
    // WHEN  they open Members and add Maruf by phone, joining 21 Nov 2026
    // THEN  Maruf shows in the members list
    worker.use(loggedInAs('owner'), ...membersApi());

    await visit('/members');
    await fillIn('[data-test-add-member-name]', 'Maruf');
    await fillIn('[data-test-add-member-contact]', '01812 345678');
    await fillIn('[data-test-add-member-joined-on]', '2026-11-21');
    await click('[data-test-add-member-submit]');

    assert.dom('[data-test-member-row]').exists({ count: 2 });
    assert.dom('[data-test-member-row="Maruf"]').exists();
  });

  test('owner opens Edit for a member, then cancels without saving', async function (assert) {
    // GIVEN the owner and Maruf; the API would save any change
    // WHEN  the owner presses Edit on Maruf, changes his name, then Cancel
    // THEN  an "Edit Maruf" tab showed his details; after Cancel it is gone,
    //       the add form is back and nothing was sent
    let sent = 0;
    worker.use(
      loggedInAs('owner'),
      ...membersApi([owner, member()]),
      http.patch('*/api/v1/members/:id', () => {
        sent += 1;
        return HttpResponse.json({ success: true, message: 'Changed' });
      }),
    );

    await visit('/members');
    await click('[data-test-edit-member="Maruf"]');
    assert.dom('[data-test-member-form-tab="edit"]').hasText('Edit Maruf');
    assert.dom('[data-test-edit-member-name]').hasValue('Maruf');
    assert.dom('[data-test-add-member-form]').doesNotExist();
    await fillIn('[data-test-edit-member-name]', 'Maruf Hossain');
    await click('[data-test-edit-member-cancel]');

    assert.dom('[data-test-member-form-tab="edit"]').doesNotExist();
    assert.dom('[data-test-edit-member-form]').doesNotExist();
    assert.dom('[data-test-add-member-form]').exists();
    assert.strictEqual(sent, 0);
  });

  test('owner switches between the add form and an open edit', async function (assert) {
    // GIVEN the owner and Maruf
    // WHEN  the owner presses Edit on Maruf, then the "Add member" tab,
    //       then the "Edit Maruf" tab
    // THEN  the add form shows with the Edit tab still there, then Maruf's
    //       edit form is back
    worker.use(loggedInAs('owner'), ...membersApi([owner, member()]));

    await visit('/members');
    await click('[data-test-edit-member="Maruf"]');
    await click('[data-test-member-form-tab="add"]');

    assert.dom('[data-test-add-member-form]').exists();
    assert.dom('[data-test-edit-member-form]').doesNotExist();
    assert.dom('[data-test-member-form-tab="add"]').hasAria('selected', 'true');
    assert.dom('[data-test-member-form-tab="edit"]').exists();

    await click('[data-test-member-form-tab="edit"]');

    assert.dom('[data-test-edit-member-name]').hasValue('Maruf');
    assert.dom('[data-test-add-member-form]').doesNotExist();
  });

  test('saving an edit closes the Edit tab', async function (assert) {
    // GIVEN the owner and Maruf; the API saves the change
    // WHEN  the owner edits Maruf's name and saves
    // THEN  the Edit tab closes and the add form is back
    worker.use(
      loggedInAs('owner'),
      ...membersApi([owner, member()]),
      http.patch('*/api/v1/members/:id', () =>
        HttpResponse.json({
          success: true,
          message: 'Member changed',
          data: member({ name: 'Maruf Hossain' }),
        }),
      ),
    );

    await visit('/members');
    await click('[data-test-edit-member="Maruf"]');
    await fillIn('[data-test-edit-member-name]', 'Maruf Hossain');
    await click('[data-test-edit-member-submit]');

    assert.dom('[data-test-member-form-tab]').doesNotExist();
    assert.dom('[data-test-add-member-form]').exists();
  });

  test('editing another member starts from their details', async function (assert) {
    // GIVEN the owner, Maruf and Hijam
    // WHEN  the owner edits Maruf, types a new name, then presses Edit on Hijam
    // THEN  the form shows Hijam's name, not what was typed for Maruf
    const hijam = member({
      id: '01a1fd00-0000-7000-8000-000000000011',
      name: 'Hijam Shusil',
      phone: '+8801912345678',
    });
    worker.use(loggedInAs('owner'), ...membersApi([owner, member(), hijam]));

    await visit('/members');
    await click('[data-test-edit-member="Maruf"]');
    await fillIn('[data-test-edit-member-name]', 'Maruf Hossain');
    await click('[data-test-edit-member="Hijam Shusil"]');

    assert
      .dom('[data-test-member-form-tab="edit"]')
      .hasText('Edit Hijam Shusil');
    assert.dom('[data-test-edit-member-name]').hasValue('Hijam Shusil');
  });

  test('a member has no Members link, and opening Members sends them home', async function (assert) {
    // GIVEN Maruf, a member (not the owner or a manager), is logged in
    // WHEN  he looks at the shell, and opens /members
    // THEN  there is no Members link, and he is sent to his home
    worker.use(loggedInAs('member'), ...membersApi());

    await visit('/');
    assert.dom('[data-test-nav-members]').doesNotExist();
    await visit('/members');

    assert.strictEqual(currentURL(), '/');
  });
});
