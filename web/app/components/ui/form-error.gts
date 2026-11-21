import type { TOC } from '@ember/component/template-only';

interface FormErrorSignature {
  Element: HTMLParagraphElement;
  Blocks: { default: [] };
}

/** Why a form wasn't accepted, read out by screen readers (`role="alert"`). */
const FormError: TOC<FormErrorSignature> = <template>
  <p
    role="alert"
    class="rounded-xl bg-owes-tint px-3 py-2 text-sm text-owes-ink"
    ...attributes
  >{{yield}}</p>
</template>;

export default FormError;
