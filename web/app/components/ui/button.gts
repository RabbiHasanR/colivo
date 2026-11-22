import type { TOC } from '@ember/component/template-only';

type Variant = 'primary' | 'secondary' | 'outline' | 'link' | 'danger-link';
type Size = 'md' | 'lg';

interface ButtonSignature {
  Element: HTMLButtonElement;
  Args: { variant?: Variant; size?: Size };
  Blocks: { default: [] };
}

// At least 44px tall: the design's minimum tap target (--spacing-touch).
const BASE =
  'inline-flex items-center justify-center gap-2 font-semibold ' +
  'whitespace-nowrap transition-colors focus-visible:outline-2 ' +
  'focus-visible:outline-offset-2 focus-visible:outline-primary ' +
  'disabled:cursor-not-allowed disabled:opacity-50';

const VARIANTS: Record<Variant, string> = {
  primary: 'bg-primary px-[18px] text-white hover:bg-primary-hover',
  secondary: 'border border-field bg-surface px-[18px] text-ink hover:bg-page',
  outline:
    'border border-primary bg-surface px-[18px] text-primary hover:bg-primary-tint',
  // Text actions in a row ("Roles · Deactivate"); still 44px tall to tap.
  link: 'min-h-touch px-1 text-[13px] text-primary hover:text-primary-hover',
  'danger-link': 'min-h-touch px-1 text-[13px] text-owes hover:text-owes-ink',
};

// md: most buttons. lg: a form's main action (48px, 12px corners).
// Text links set their own height and size, so they take no size.
const SIZES: Record<Size, string> = {
  md: 'min-h-touch rounded-field text-sm',
  lg: 'min-h-12 rounded-xl text-[15px]',
};

/** A button's classes, also for a link that looks like one. */
export function buttonClasses(
  variant: Variant = 'primary',
  size: Size = 'md',
): string {
  const isLink = variant === 'link' || variant === 'danger-link';
  return `${BASE} ${VARIANTS[variant]} ${isLink ? '' : SIZES[size]}`;
}

/**
 * <Button @variant="secondary" {{on "click" this.toggle}} data-test-menu-button>
 *   Menu
 * </Button>
 * <Button type="submit" @size="lg">Log in</Button>
 */
const Button: TOC<ButtonSignature> = <template>
  <button type="button" class={{buttonClasses @variant @size}} ...attributes>
    {{yield}}
  </button>
</template>;

export default Button;
