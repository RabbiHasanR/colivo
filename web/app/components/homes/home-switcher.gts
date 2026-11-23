import Component from '@glimmer/component';
import { tracked } from '@glimmer/tracking';
import { action } from '@ember/object';
import { fn } from '@ember/helper';
import { on } from '@ember/modifier';
import { guidFor } from '@ember/object/internals';
import { modifier } from 'ember-modifier';
import type { HomeChoice } from '../../services/current-home';

interface HomeSwitcherSignature {
  Element: HTMLDivElement;
  Args: {
    /** The home this tab is in. */
    current: { id: string; name: string };
    /** All of the person's homes; the current one isn't offered. */
    homes: HomeChoice[];
    onChoose: (homeId: string) => void;
  };
}

/** Puts focus on the menu's first item when it opens. */
const focusFirst = modifier((menu: HTMLElement) => {
  menu.querySelector<HTMLElement>('[role="menuitem"]')?.focus();
});

/**
 * The home name in the shell, as a button that opens a menu of the
 * person's other homes (Phase 1b). Follows the ARIA menu button pattern:
 * arrow keys move between homes, Escape closes and focus goes back to the
 * button.
 */
export default class HomeSwitcher extends Component<HomeSwitcherSignature> {
  @tracked isOpen = false;

  readonly menuId = `${guidFor(this)}-homes`;

  get otherHomes(): HomeChoice[] {
    return this.args.homes.filter((home) => home.id !== this.args.current.id);
  }

  @action
  toggle(): void {
    this.isOpen = !this.isOpen;
  }

  @action
  choose(homeId: string): void {
    this.isOpen = false;
    this.args.onChoose(homeId);
  }

  /** Arrow keys move between homes; Escape closes, back on the button. */
  @action
  onKeydown(event: KeyboardEvent): void {
    const menu = (event.currentTarget as HTMLElement).closest('[role="menu"]');
    if (!menu) return;
    const items = [...menu.querySelectorAll<HTMLElement>('[role="menuitem"]')];
    const at = items.indexOf(document.activeElement as HTMLElement);
    if (event.key === 'Escape') {
      this.isOpen = false;
      menu.parentElement
        ?.querySelector<HTMLElement>('[aria-haspopup="menu"]')
        ?.focus();
    } else if (event.key === 'ArrowDown' || event.key === 'ArrowUp') {
      const step = event.key === 'ArrowDown' ? 1 : -1;
      items[(at + step + items.length) % items.length]?.focus();
    } else {
      return;
    }
    event.preventDefault();
  }

  <template>
    <div class="relative" ...attributes>
      <button
        type="button"
        aria-haspopup="menu"
        aria-controls={{this.menuId}}
        aria-expanded={{if this.isOpen "true" "false"}}
        class="flex min-h-touch items-center gap-1 rounded-field text-left text-xs text-muted hover:text-ink"
        data-test-home-switcher
        {{on "click" this.toggle}}
      ><span class="truncate">{{@current.name}}</span><svg
          class="size-3.5 shrink-0"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
          aria-hidden="true"
        ><path d="M6 9l6 6 6-6" /></svg></button>
      {{#if this.isOpen}}
        <ul
          id={{this.menuId}}
          role="menu"
          aria-label="Switch home"
          class="absolute top-full left-0 z-10 mt-1 flex min-w-52 flex-col rounded-field border border-line bg-surface p-1 shadow-lg"
          {{focusFirst}}
        >
          {{#each this.otherHomes as |home|}}
            <li role="none"><button
                type="button"
                role="menuitem"
                class="flex min-h-touch w-full items-center rounded-field px-3 text-left text-sm hover:bg-page focus:bg-page"
                data-test-home-switch={{home.name}}
                {{on "click" (fn this.choose home.id)}}
                {{on "keydown" this.onKeydown}}
              >{{home.name}}</button></li>
          {{/each}}
        </ul>
      {{/if}}
    </div>
  </template>
}
