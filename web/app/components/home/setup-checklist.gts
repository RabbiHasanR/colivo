import type { TOC } from '@ember/component/template-only';
import type { SetupStep } from '../../services/current-home';

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

function title(key: string): string {
  return WORDS[key]?.title ?? key;
}

function hint(key: string): string {
  return WORDS[key]?.hint ?? '';
}

function doneCount(steps: SetupStep[]): number {
  return steps.filter((step) => step.done).length;
}

/** "Set up your home" (FR-95): what a new home still needs, in order. */
const SetupChecklist: TOC<SetupChecklistSignature> = <template>
  <section data-test-setup-checklist aria-labelledby="setup-title">
    <h2 id="setup-title">Set up your home</h2>
    <p data-test-setup-progress>{{doneCount @steps}}
      of
      {{@steps.length}}
      done</p>
    <ol>
      {{#each @steps as |step|}}
        <li
          data-test-setup-step={{step.key}}
          data-test-done={{if step.done ""}}
        >
          {{if step.done "✓ "}}{{title step.key}}
          <p>{{hint step.key}}</p>
        </li>
      {{/each}}
    </ol>
  </section>
</template>;

export default SetupChecklist;
