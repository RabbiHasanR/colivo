import { module, test } from 'qunit';
import { render } from '@ember/test-helpers';
import { setupRenderingTest } from 'colivo-web/tests/helpers';
import EmptyState from 'colivo-web/components/home/empty-state';

module('Integration | Component | home/empty-state', function (hooks) {
  setupRenderingTest(hooks);

  test('says what will appear, and offers its one action only when given', async function (assert) {
    // GIVEN an empty list with a reason, once with an action and once without
    // WHEN  its empty state is rendered
    // THEN  the title and reason show, and the action only when there is one
    await render(
      <template>
        <EmptyState
          @title="Today's meals"
          @reason="Only you so far."
          data-test-with-action
        >
          <:action><a href="#">Add members</a></:action>
        </EmptyState>
        <EmptyState
          @title="All caught up"
          @reason="Payments to confirm show here."
          data-test-without-action
        />
      </template>,
    );

    assert
      .dom('[data-test-with-action] [data-test-empty-state-title]')
      .hasText("Today's meals");
    assert
      .dom('[data-test-with-action] [data-test-empty-state-reason]')
      .hasText('Only you so far.');
    assert
      .dom('[data-test-with-action] [data-test-empty-state-action]')
      .hasText('Add members');
    assert
      .dom('[data-test-without-action] [data-test-empty-state-title]')
      .hasText('All caught up');
    assert
      .dom('[data-test-without-action] [data-test-empty-state-action]')
      .doesNotExist();
  });
});
