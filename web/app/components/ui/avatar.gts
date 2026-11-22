import type { TOC } from '@ember/component/template-only';
import { initials } from '../../utils/names';

type Size = 'sm' | 'md';

interface AvatarSignature {
  Element: HTMLSpanElement;
  /** `@faded`: someone who no longer lives in the home (grey). */
  Args: { name: string; size?: Size; faded?: boolean };
}

// sm: a table row (32px). md: the sidebar's profile card (36px).
const SIZES: Record<Size, string> = {
  sm: 'size-8 text-xs',
  md: 'size-9 text-[13px]',
};

function classes(size: Size = 'sm', faded = false): string {
  const colour = faded
    ? 'bg-page text-ink-soft'
    : 'bg-tag-prepaid text-tag-prepaid-ink';
  return `inline-flex shrink-0 items-center justify-center rounded-full font-semibold ${SIZES[size]} ${colour}`;
}

/**
 * A person's initials in a circle (colivo-design/web). Decorative: the name
 * is always written beside it.
 */
const Avatar: TOC<AvatarSignature> = <template>
  <span aria-hidden="true" class={{classes @size @faded}} ...attributes>
    {{initials @name}}
  </span>
</template>;

export default Avatar;
