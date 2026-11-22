import Component from '@glimmer/component';
import { tracked } from '@glimmer/tracking';
import { action } from '@ember/object';
import { on } from '@ember/modifier';
import { guidFor } from '@ember/object/internals';
import { service } from '@ember/service';
import { LinkTo } from '@ember/routing';
import type RouterService from '@ember/routing/router-service';
import type SessionService from '../../services/session';
import { roleLabel } from '../../utils/roles';
import Avatar from '../ui/avatar';
import Button from '../ui/button';

// A sidebar link; the current page's is teal (LinkTo adds `active`).
const NAV_LINK =
  'flex min-h-touch items-center gap-2.5 rounded-field px-3 text-sm ' +
  'font-medium text-ink-soft hover:bg-page ' +
  '[&.active]:bg-primary-tint [&.active]:font-semibold [&.active]:text-primary';

interface AppShellSignature {
  Blocks: { default: [] };
}

/**
 * The page frame from colivo-design/web/WebHomeEmpty.html: a sidebar beside
 * the content from 1024px up; below that, a top bar whose menu button opens
 * and closes the sidebar above the content. Each phase adds its nav links.
 */
export default class AppShell extends Component<AppShellSignature> {
  @service declare session: SessionService;
  @service declare router: RouterService;

  @tracked isMenuOpen = false;

  readonly sidebarId = `${guidFor(this)}-sidebar`;

  @action
  toggleMenu(): void {
    this.isMenuOpen = !this.isMenuOpen;
  }

  @action
  async logOut(): Promise<void> {
    await this.session.logOut();
    this.router.transitionTo('log-in');
  }

  <template>
    <div data-test-app-shell class="min-h-screen lg:flex">
      <header
        class="flex items-center justify-between border-b border-line bg-surface px-4 py-2 lg:hidden"
      >
        <span class="font-display text-lg font-bold text-primary">Colivo</span>
        <Button
          @variant="secondary"
          aria-controls={{this.sidebarId}}
          aria-expanded={{if this.isMenuOpen "true" "false"}}
          data-test-menu-button
          {{on "click" this.toggleMenu}}
        >
          Menu
        </Button>
      </header>

      <nav
        id={{this.sidebarId}}
        aria-label="Main"
        data-test-sidebar
        data-open={{if this.isMenuOpen "true" "false"}}
        class="hidden flex-col gap-[18px] border-b border-line bg-surface px-3.5 py-5 data-[open=true]:flex lg:sticky lg:top-0 lg:flex lg:h-screen lg:w-58 lg:shrink-0 lg:border-r lg:border-b-0"
      >
        <div class="hidden flex-col gap-0.5 px-2 lg:flex">
          <span
            class="font-display text-lg font-bold text-primary"
          >Colivo</span>
          {{#if this.session.me}}
            <span class="text-xs text-muted" data-test-shell-home>
              {{this.session.me.home.name}}
            </span>
          {{/if}}
        </div>
        {{#if this.session.me}}
          <ul class="flex flex-col gap-1">
            <li><LinkTo
                @route="authenticated.index"
                class={{NAV_LINK}}
                data-test-nav-home
              ><svg
                  class="size-5"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="1.8"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  aria-hidden="true"
                ><path
                    d="M3 11l9-7 9 7v9a1 1 0 0 1-1 1h-5v-6h-6v6H4a1 1 0 0 1-1-1z"
                  /></svg>Home</LinkTo></li>
            {{#if this.session.isOwnerOrManager}}
              <li><LinkTo
                  @route="authenticated.members"
                  class={{NAV_LINK}}
                  data-test-nav-members
                ><svg
                    class="size-5"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="1.8"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    aria-hidden="true"
                  ><circle cx="9" cy="8" r="3.5" /><path
                      d="M2.5 20c1-3.5 3.6-5.5 6.5-5.5s5.5 2 6.5 5.5"
                    /><circle cx="17" cy="9" r="2.5" /><path
                      d="M17 14c2.3 0 4 1.5 4.5 4.5"
                    /></svg>Members</LinkTo></li>
            {{/if}}
          </ul>
          <div class="mt-auto flex flex-col gap-1">
            <div class="flex items-center gap-2.5 rounded-xl bg-page p-2.5">
              <Avatar @name={{this.session.me.membership.name}} @size="md" />
              {{! One text for screen readers: "Rabbi Hasan · Owner". }}
              <span class="flex min-w-0 flex-col" data-test-shell-person>
                <span
                  class="truncate text-[13px] font-semibold"
                >{{this.session.me.membership.name}}</span>
                <span class="sr-only"> · </span>
                <span class="text-[11px] text-muted">{{roleLabel
                    this.session.me.membership.role
                  }}</span>
              </span>
            </div>
            <button
              type="button"
              class="min-h-touch rounded-field px-3 text-left text-sm font-medium text-ink-soft hover:bg-page"
              data-test-log-out
              {{on "click" this.logOut}}
            >Log out</button>
          </div>
        {{/if}}
      </nav>

      <main class="min-w-0 flex-1 px-4 pt-7 pb-10 sm:px-6 lg:px-10">
        <div class="mx-auto flex w-full max-w-[1180px] flex-col gap-5">
          {{yield}}
        </div>
      </main>
    </div>
  </template>
}
