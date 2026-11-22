import Component from '@glimmer/component';
import { tracked } from '@glimmer/tracking';
import { action } from '@ember/object';
import { service } from '@ember/service';
import type RouterService from '@ember/routing/router-service';
import { fn } from '@ember/helper';
import { on } from '@ember/modifier';
import { eq } from '../../utils/template';
import { SEGMENT_TRACK, segmentClasses } from '../ui/segment-classes';
import LogInForm from './log-in-form';
import SignUpForm from './sign-up-form';

type Tab = 'log-in' | 'create-home';

const TABS: Array<{ key: Tab; label: string }> = [
  { key: 'log-in', label: 'Log in' },
  { key: 'create-home', label: 'Create a home' },
];

/**
 * Log in or create a home (colivo-design/web/WebAuth.html): one above the
 * other on a phone, side by side on a wide screen (checked by eye).
 */
export default class LogInPage extends Component {
  @service declare router: RouterService;

  @tracked tab: Tab = 'log-in';

  /** Filled from "Not added yet" → "Create my own home". */
  @tracked signUpContact: string | null = null;

  readonly tabs = TABS;

  @action
  show(tab: Tab): void {
    this.tab = tab;
  }

  @action
  createHome(contact: string): void {
    this.signUpContact = contact;
    this.tab = 'create-home';
  }

  @action
  goHome(): void {
    this.router.transitionTo('authenticated.index');
  }

  <template>
    <div class="flex min-h-screen flex-wrap items-stretch">
      <section
        aria-label="About Colivo"
        class="flex flex-[1_1_420px] flex-col justify-between gap-7 bg-primary p-[clamp(28px,5vw,64px)] text-white"
      >
        <span class="font-display text-xl font-bold">Colivo</span>
        <div class="flex max-w-[520px] flex-col gap-4">
          <h1
            class="text-[clamp(30px,3.4vw,46px)] leading-[1.1] font-semibold"
          >Meals, groceries, rent and bills for your shared home. No
            spreadsheet.</h1>
          <p class="text-base leading-relaxed opacity-90">Everyone logs their
            own meals, uploads receipts and sees what they owe. The month closes
            with one tap.</p>
        </div>
        <ul class="flex flex-wrap gap-x-[22px] gap-y-2.5 text-sm opacity-90">
          <li>✓ Cost per meal, worked out live</li>
          <li>✓ Grocery fund and bills</li>
          <li>✓ Deposits and notice periods</li>
        </ul>
      </section>

      <main
        class="flex flex-[1_1_480px] items-center justify-center px-4 py-6 sm:px-14 sm:py-16"
      >
        <div class="flex w-full max-w-[440px] flex-col gap-[18px]">
          <div
            role="tablist"
            aria-label="Log in or create a home"
            class="{{SEGMENT_TRACK}} grid grid-cols-2"
          >
            {{#each this.tabs as |tab|}}
              <button
                type="button"
                role="tab"
                id="auth-tab-{{tab.key}}"
                aria-controls="auth-panel"
                aria-selected={{if (eq this.tab tab.key) "true" "false"}}
                class="{{segmentClasses (eq this.tab tab.key)}} min-h-[42px]"
                data-test-auth-tab={{tab.key}}
                {{on "click" (fn this.show tab.key)}}
              >{{tab.label}}</button>
            {{/each}}
          </div>
          <div
            id="auth-panel"
            role="tabpanel"
            aria-labelledby="auth-tab-{{this.tab}}"
          >
            {{#if (eq this.tab "log-in")}}
              <section
                class="flex flex-col gap-[18px]"
                data-test-log-in
                aria-labelledby="log-in-title"
              >
                <div class="flex flex-col gap-1.5">
                  <h2 id="log-in-title" class="text-[28px] font-semibold">Log in</h2>
                  <p class="text-sm leading-normal text-muted">Use the phone or
                    email you signed up with, or the one your home's manager
                    added you with. No home code needed.</p>
                </div>
                <LogInForm
                  @onLoggedIn={{this.goHome}}
                  @onCreateHome={{this.createHome}}
                />
                <p class="text-[13px] leading-normal text-muted">Not added yet?
                  Ask your home's owner or manager to add your number. You'll
                  get an SMS or email when it's done.</p>
              </section>
            {{else}}
              <section
                class="flex flex-col gap-[18px]"
                data-test-create-home
                aria-labelledby="create-home-title"
              >
                <div class="flex flex-col gap-1.5">
                  <h2
                    id="create-home-title"
                    class="text-[28px] font-semibold"
                  >Create your home</h2>
                  <p class="text-sm leading-normal text-muted">For the person
                    who runs the home. You'll be the owner and can add members
                    afterwards.</p>
                </div>
                <SignUpForm
                  @contact={{this.signUpContact}}
                  @onSignedUp={{this.goHome}}
                />
                <p class="text-[13px] leading-normal text-muted">Already in a
                  home? You can still create your own, and choose between them
                  when you log in.</p>
              </section>
            {{/if}}
          </div>
        </div>
      </main>
    </div>
  </template>
}
