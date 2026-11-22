import type { TOC } from '@ember/component/template-only';
import { LinkTo } from '@ember/routing';
import EmptyState from '../../components/home/empty-state';
import SetupChecklist from '../../components/home/setup-checklist';
import StatCard from '../../components/home/stat-card';
import Welcome from '../../components/home/welcome';
import { buttonClasses } from '../../components/ui/button';
import type { HomeModel } from '../../routes/authenticated/index';

/**
 * A home page (colivo-design/web/WebHomeEmpty.html). The numbers are empty
 * until their phases record them.
 */
const HomeTemplate: TOC<{ Args: { model: HomeModel } }> = <template>
  <Welcome @me={{@model.me}} @month={{@model.month}} />
  <div class="flex flex-wrap gap-3">
    <StatCard
      @label="Home fund"
      @value="৳0"
      @note="No payments yet"
      @empty={{true}}
    />
    <StatCard
      @label="Cost per meal"
      @value="—"
      @note="Shows after the first groceries"
      @empty={{true}}
    />
    <StatCard
      @label="Groceries"
      @value="৳0"
      @note={{@model.month}}
      @empty={{true}}
    />
    <StatCard
      @label="Bills to pay"
      @value="৳0"
      @note="Add bills in settings"
      @empty={{true}}
    />
  </div>
  <div class="flex flex-wrap items-start gap-4">
    {{#if @model.setup}}
      <div class="flex min-w-0 flex-[999_1_640px] flex-col gap-4">
        <SetupChecklist @steps={{@model.setup.steps}} />
      </div>
    {{/if}}
    <div class="flex min-w-0 flex-[1_1_320px] flex-col gap-4">
      <EmptyState
        @title="Today's meals"
        @reason="Only you so far. Add members and everyone's meals show here, with how many to cook for."
        data-test-empty-state="meals"
      >
        <:action>
          {{#if @model.runsHome}}
            <LinkTo
              @route="authenticated.members"
              class={{(buttonClasses)}}
              data-test-add-members
            >Add members</LinkTo>
          {{/if}}
        </:action>
      </EmptyState>
      <EmptyState
        @title="All caught up"
        @reason="Payments to confirm and notices show here once members join."
        data-test-empty-state="inbox"
      />
    </div>
  </div>
</template>;

export default HomeTemplate;
