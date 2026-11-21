import type { TOC } from '@ember/component/template-only';
import EmptyState from '../../components/home/empty-state';
import SetupChecklist from '../../components/home/setup-checklist';
import Welcome from '../../components/home/welcome';
import type { HomeModel } from '../../routes/authenticated/index';

/** A home page (colivo-design/web/WebHomeEmpty.html). */
const HomeTemplate: TOC<{ Args: { model: HomeModel } }> = <template>
  <Welcome @me={{@model.me}} />
  {{#if @model.setup}}
    <SetupChecklist @steps={{@model.setup.steps}} />
  {{/if}}
  <EmptyState
    @title="Today's meals"
    @reason="Only you so far. Add members and everyone's meals show here, with how many to cook for."
    data-test-empty-state="meals"
  />
  <EmptyState
    @title="All caught up"
    @reason="Payments to confirm and notices show here once members join."
    data-test-empty-state="inbox"
  />
</template>;

export default HomeTemplate;
