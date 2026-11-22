import type { TOC } from '@ember/component/template-only';

interface CardSignature {
  Element: HTMLElement;
  Blocks: { default: [] };
}

/**
 * The white surface every block of a page sits on (colivo-design/web: white,
 * 1px border, 16px corners). Padding and layout come from the caller:
 * `<Card class="flex flex-col gap-3 p-5">…</Card>`.
 */
const Card: TOC<CardSignature> = <template>
  <section
    class="rounded-card border border-line bg-surface"
    ...attributes
  >{{yield}}</section>
</template>;

export default Card;
