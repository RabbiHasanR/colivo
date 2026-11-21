import type { TOC } from '@ember/component/template-only';

interface EmptyStateSignature {
  Element: HTMLElement;
  Args: { title: string; reason: string };
  Blocks: { action: [] };
}

/**
 * What an empty list shows instead of nothing (FR-95,
 * colivo-design/mobile/EmptyStates.html): a short reason and, where it
 * helps, the one action that fills it.
 *
 *   <EmptyState @title="Today's meals" @reason="Only you so far.">
 *     <:action><LinkTo …>Add members</LinkTo></:action>
 *   </EmptyState>
 */
const EmptyState: TOC<EmptyStateSignature> = <template>
  <section ...attributes>
    <h2 data-test-empty-state-title>{{@title}}</h2>
    <p data-test-empty-state-reason>{{@reason}}</p>
    {{#if (has-block "action")}}
      <div data-test-empty-state-action>{{yield to="action"}}</div>
    {{/if}}
  </section>
</template>;

export default EmptyState;
