import type { TOC } from '@ember/component/template-only';

interface ScrollBoxSignature {
  Element: HTMLDivElement;
  Blocks: { default: [] };
}

/** A wide table scrolls inside this box, never the page (Responsive design). */
const ScrollBox: TOC<ScrollBoxSignature> = <template>
  <div class="max-w-full overflow-x-auto" ...attributes>{{yield}}</div>
</template>;

export default ScrollBox;
