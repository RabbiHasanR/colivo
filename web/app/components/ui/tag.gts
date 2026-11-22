import type { TOC } from '@ember/component/template-only';

export type TagTone = 'dark' | 'blue' | 'teal' | 'amber' | 'brown' | 'grey';

interface TagSignature {
  Element: HTMLSpanElement;
  Args: { tone?: TagTone };
  Blocks: { default: [] };
}

// The pill colours used for roles and statuses in colivo-design/web.
const TONES: Record<TagTone, string> = {
  dark: 'bg-ink text-white',
  blue: 'bg-tag-prepaid text-tag-prepaid-ink',
  teal: 'bg-primary-tint text-primary-hover',
  amber: 'bg-tag-grocery-fund text-tag-grocery-fund-ink',
  brown: 'bg-owes-tint text-owes-ink',
  grey: 'bg-tag-rent text-tag-rent-ink',
};

function classes(tone: TagTone = 'grey'): string {
  return `inline-flex rounded-full px-2 py-[3px] text-[11px] font-semibold whitespace-nowrap ${TONES[tone]}`;
}

/** A small pill: `<Tag @tone="teal">Active</Tag>` */
const Tag: TOC<TagSignature> = <template>
  <span class={{classes @tone}} ...attributes>{{yield}}</span>
</template>;

export default Tag;
