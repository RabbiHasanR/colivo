import Component from '@glimmer/component';
import { tracked } from '@glimmer/tracking';
import { on } from '@ember/modifier';
import { guidFor } from '@ember/object/internals';
import Button from '../ui/button';

interface AppShellSignature {
  Blocks: { default: [] };
}

/**
 * The page frame from colivo-design/web/WebHomeEmpty.html: a sidebar beside
 * the content from 1024px up; below that, a top bar whose menu button opens
 * and closes the sidebar above the content. Each phase adds its nav links.
 */
export default class AppShell extends Component<AppShellSignature> {
  @tracked isMenuOpen = false;

  readonly sidebarId = `${guidFor(this)}-sidebar`;

  toggleMenu = (): void => {
    this.isMenuOpen = !this.isMenuOpen;
  };

  <template>
    <div data-test-app-shell class="min-h-screen lg:flex">
      <header
        class="flex items-center justify-between border-b border-line bg-surface px-4 py-2 lg:hidden"
      >
        <span
          class="font-display text-lg font-semibold text-primary"
        >Colivo</span>
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
        class="hidden border-b border-line bg-surface p-4 data-[open=true]:block lg:block lg:w-64 lg:shrink-0 lg:border-r lg:border-b-0"
      >
        <span
          class="hidden font-display text-lg font-semibold text-primary lg:block"
        >Colivo</span>
      </nav>

      <main class="min-w-0 flex-1 p-4 lg:p-8">
        {{yield}}
      </main>
    </div>
  </template>
}
