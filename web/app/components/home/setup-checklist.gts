import type { TOC } from '@ember/component/template-only';
import { LinkTo } from '@ember/routing';
import type { SetupStep } from '../../services/current-home';
import Card from '../ui/card';

interface SetupChecklistSignature {
  Args: { steps: SetupStep[] };
}

/** Each step's words, from colivo-design/web/WebHomeEmpty.html. */
const WORDS: Record<string, { title: string; hint: string }> = {
  home_created: { title: 'Home created', hint: 'You are the owner' },
  members: {
    title: 'Add members',
    hint: 'By phone or email · they get an SMS or email',
  },
  rooms: {
    title: 'Add rooms and rent',
    hint: "Landlord rent and each room's share",
  },
  rules: { title: 'Set home rules', hint: 'Deposit, notice period, rent gaps' },
  bills: { title: 'Add bills', hint: 'Electricity, gas, internet, cook…' },
};

/** The page each step is done on; a step's phase adds it with the page. */
const ROUTES: Record<string, string> = {
  members: 'authenticated.members',
};

function title(key: string): string {
  return WORDS[key]?.title ?? key;
}

function hint(key: string): string {
  return WORDS[key]?.hint ?? '';
}

function routeFor(step: SetupStep): string | undefined {
  return step.done ? undefined : ROUTES[step.key];
}

function doneCount(steps: SetupStep[]): number {
  return steps.filter((step) => step.done).length;
}

function progressStyle(steps: SetupStep[]): string {
  const percent = steps.length ? (doneCount(steps) / steps.length) * 100 : 0;
  return `width: ${percent}%`;
}

/** "Set up your home" (FR-95): what a new home still needs, in order. */
const SetupChecklist: TOC<SetupChecklistSignature> = <template>
  <Card
    class="overflow-hidden"
    data-test-setup-checklist
    aria-labelledby="setup-title"
  >
    <div class="flex flex-col gap-2.5 px-[18px] pt-4 pb-3">
      <div class="flex items-baseline justify-between gap-3">
        <h2 id="setup-title" class="font-sans text-[17px] font-semibold">Set up
          your home</h2>
        <span class="text-[13px] text-muted" data-test-setup-progress>
          {{doneCount @steps}}
          of
          {{@steps.length}}
          done
        </span>
      </div>
      <div
        role="progressbar"
        aria-label="Setup progress"
        aria-valuemin="0"
        aria-valuemax={{@steps.length}}
        aria-valuenow={{doneCount @steps}}
        class="h-1.5 overflow-hidden rounded-full bg-tag-rent"
      >
        <div class="h-full bg-primary" style={{progressStyle @steps}}></div>
      </div>
    </div>
    <ol>
      {{#each @steps as |step|}}
        <li
          class="flex min-h-15 items-center gap-3.5 border-t border-divider px-[18px] py-2 first:border-t-0"
          data-test-setup-step={{step.key}}
          data-test-done={{if step.done ""}}
        >
          {{#if step.done}}
            <span
              aria-hidden="true"
              class="flex size-6.5 shrink-0 items-center justify-center rounded-full bg-primary text-[13px] font-bold text-white"
            >✓</span>
          {{else}}
            <span
              aria-hidden="true"
              class="size-6.5 shrink-0 rounded-full border-2 border-check"
            ></span>
          {{/if}}
          <span class="flex flex-1 flex-col gap-0.5">
            <span
              class="text-[15px] font-semibold
                {{if step.done 'text-muted line-through'}}"
            >{{#if step.done}}<span class="sr-only">Done: </span>{{/if}}{{title
                step.key
              }}</span>
            <span class="text-[13px] text-muted">{{hint step.key}}</span>
          </span>
          {{#let (routeFor step) as |route|}}
            {{#if route}}
              <LinkTo
                @route={{route}}
                class="flex min-h-touch items-center text-sm font-semibold text-primary hover:text-primary-hover"
                aria-label="Start: {{title step.key}}"
                data-test-setup-start={{step.key}}
              >Start ›</LinkTo>
            {{/if}}
          {{/let}}
        </li>
      {{/each}}
    </ol>
  </Card>
</template>;

export default SetupChecklist;
