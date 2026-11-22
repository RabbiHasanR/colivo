import type { TOC } from '@ember/component/template-only';

interface ScrollBoxSignature {
  Element: HTMLDivElement;
  Blocks: { default: [] };
}

/**
 * A wide table scrolls inside this box, never the page (Responsive design).
 * `relative` keeps absolutely placed children (an `sr-only` header) inside
 * it too; without it they widen the page.
 */
const ScrollBox: TOC<ScrollBoxSignature> = <template>
  <div class="relative max-w-full overflow-x-auto" ...attributes>{{yield}}</div>
</template>;

export default ScrollBox;
