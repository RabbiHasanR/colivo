import type { TOC } from '@ember/component/template-only';

type Variant = 'primary' | 'secondary';

interface ButtonSignature {
  Element: HTMLButtonElement;
  Args: { variant?: Variant };
  Blocks: { default: [] };
}

// At least 44px tall: the design's minimum tap target (--spacing-touch).
const BASE =
  'inline-flex min-h-touch items-center justify-center gap-2 rounded-xl px-4 ' +
  'text-sm font-medium transition-colors focus-visible:outline-2 ' +
  'focus-visible:outline-offset-2 focus-visible:outline-primary ' +
  'disabled:cursor-not-allowed disabled:opacity-50';

const VARIANTS: Record<Variant, string> = {
  primary: 'bg-primary text-white hover:bg-primary-hover',
  secondary: 'border border-line bg-surface text-ink hover:bg-page',
};

function classes(variant: Variant = 'primary'): string {
  return `${BASE} ${VARIANTS[variant]}`;
}

/**
 * <Button @variant="secondary" {{on "click" this.toggle}} data-test-menu-button>
 *   Menu
 * </Button>
 */
const Button: TOC<ButtonSignature> = <template>
  <button type="button" class={{classes @variant}} ...attributes>
    {{yield}}
  </button>
</template>;

export default Button;
