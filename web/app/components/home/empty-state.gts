import type { TOC } from '@ember/component/template-only';
import Card from '../ui/card';

interface EmptyStateSignature {
  Element: HTMLElement;
  Args: { title: string; reason: string };
  Blocks: { action: [] };
}

/**
 * What an empty list shows instead of nothing (FR-95,
 * colivo-design/web/WebHomeEmpty.html): a short reason and, where it
 * helps, the one action that fills it.
 *
 *   <EmptyState @title="Today's meals" @reason="Only you so far.">
 *     <:action><LinkTo …>Add members</LinkTo></:action>
 *   </EmptyState>
 */
const EmptyState: TOC<EmptyStateSignature> = <template>
  <Card
    class="flex flex-col items-center gap-2.5 px-5 py-7 text-center"
    ...attributes
  >
    <h2
      class="font-sans text-base font-semibold"
      data-test-empty-state-title
    >{{@title}}</h2>
    <p
      class="max-w-80 text-sm leading-normal text-muted"
      data-test-empty-state-reason
    >{{@reason}}</p>
    {{#if (has-block "action")}}
      <div data-test-empty-state-action>{{yield to="action"}}</div>
    {{/if}}
  </Card>
</template>;

export default EmptyState;
