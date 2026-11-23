import type { TOC } from '@ember/component/template-only';
import { fn } from '@ember/helper';
import { on } from '@ember/modifier';
import type { HomeChoice } from '../../services/current-home';
import { roleLabel, roleTone } from '../../utils/roles';
import Card from '../ui/card';
import Tag from '../ui/tag';

interface HomePickerSignature {
  Args: {
    homes: HomeChoice[];
    onChoose: (homeId: string) => void;
  };
}

/**
 * "Choose a home" (Phase 1b): one row per home with its area and the
 * person's role there, styled like the Members rows
 * (colivo-design/web/WebMembers.html). Tapping a row chooses that home.
 */
const HomePicker: TOC<HomePickerSignature> = <template>
  <Card class="overflow-hidden" data-test-home-picker>
    <ul>
      {{#each @homes as |home|}}
        <li class="border-t border-divider first:border-t-0">
          <button
            type="button"
            class="flex min-h-touch w-full items-center justify-between gap-3 px-5 py-3.5 text-left hover:bg-page"
            data-test-home-choice={{home.name}}
            {{on "click" (fn @onChoose home.id)}}
          >
            <span class="flex min-w-0 flex-col">
              <span class="truncate font-semibold">{{home.name}}</span>
              {{#if home.area}}
                <span class="text-[13px] text-muted">{{home.area}}</span>
              {{/if}}
            </span>
            <Tag @tone={{roleTone home.role}}>{{roleLabel home.role}}</Tag>
          </button>
        </li>
      {{/each}}
    </ul>
  </Card>
</template>;

export default HomePicker;
