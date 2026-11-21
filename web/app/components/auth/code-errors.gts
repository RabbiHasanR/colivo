import type { TOC } from '@ember/component/template-only';
import { on } from '@ember/modifier';
import { eq } from '../../utils/template';
import type { CodeError } from '../../utils/code-error';
import Button from '../ui/button';
import FormError from '../ui/form-error';

interface CodeErrorsSignature {
  Args: { error: CodeError; onSendNewCode: () => void };
}

/**
 * Why a one-time code was refused, and the way forward
 * (colivo-design/web/WebAuthErrors.html). Shared by log-in and sign-up.
 */
const CodeErrors: TOC<CodeErrorsSignature> = <template>
  <FormError data-test-code-error>{{@error.message}}</FormError>
  {{#if (eq @error.reason "expired")}}
    <Button
      @variant="secondary"
      data-test-send-new-code
      {{on "click" @onSendNewCode}}
    >Send a new code</Button>
  {{/if}}
</template>;

export default CodeErrors;
