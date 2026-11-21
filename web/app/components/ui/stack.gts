import type { TOC } from '@ember/component/template-only';

interface StackSignature {
  Element: HTMLDivElement;
  Blocks: { default: [] };
}

/** Children one under another, evenly spaced. */
const Stack: TOC<StackSignature> = <template>
  <div class="flex flex-col gap-4" ...attributes>{{yield}}</div>
</template>;

export default Stack;
