import type { TOC } from '@ember/component/template-only';
import { on } from '@ember/modifier';
import { modifier } from 'ember-modifier';

interface DialogSignature {
  Element: HTMLDialogElement;
  Args: { title: string; onClose: () => void };
  Blocks: { default: [] };
}

/**
 * Opens as a modal dialog when shown (FR-97: confirmations are a centred
 * dialog on the web). The browser's `showModal()` keeps focus inside it,
 * closes it on Escape and returns focus to where it was opened from.
 */
const showModal = modifier((element: HTMLDialogElement) => {
  element.showModal();
  return () => {
    if (element.open) element.close();
  };
});

function closeOnCancel(onClose: () => void) {
  return (event: Event) => {
    event.preventDefault();
    onClose();
  };
}

const Dialog: TOC<DialogSignature> = <template>
  <dialog
    class="m-auto w-full max-w-md rounded-card border border-line bg-surface p-6 text-ink backdrop:bg-ink/40"
    aria-label={{@title}}
    {{showModal}}
    {{on "cancel" (closeOnCancel @onClose)}}
    ...attributes
  >
    <h2 class="mb-4 font-display text-lg font-semibold">{{@title}}</h2>
    {{yield}}
  </dialog>
</template>;

export default Dialog;
