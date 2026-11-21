import type { TOC } from '@ember/component/template-only';
import { on } from '@ember/modifier';
import { eq } from '../../utils/template';
import { triesLeftText, type CodeError } from '../../utils/code-error';
import Button from '../ui/button';
import Countdown from '../ui/countdown';
import FormError from '../ui/form-error';

interface CodeErrorsSignature {
  Args: {
    error: CodeError;
    onSendNewCode: () => void;
    onUseDifferentContact: () => void;
  };
}

/**
 * Why a one-time code was refused, and the way forward
 * (colivo-design/web/WebAuthErrors.html). Shared by log-in and sign-up.
 */
const CodeErrors: TOC<CodeErrorsSignature> = <template>
  {{#if (eq @error.reason "locked")}}
    <FormError data-test-code-error>
      <strong>Too many wrong codes</strong>
      To keep your account safe, try again in
      <Countdown @seconds={{@error.retryInSeconds}} />. Your home's data isn't
      affected.
    </FormError>
    <Button
      @variant="secondary"
      data-test-use-different-contact
      {{on "click" @onUseDifferentContact}}
    >Use a different phone or email</Button>
  {{else}}
    <FormError data-test-code-error>
      {{@error.message}}
      {{triesLeftText @error.triesLeft}}
    </FormError>
    {{#if (eq @error.reason "expired")}}
      <Button
        @variant="secondary"
        data-test-send-new-code
        {{on "click" @onSendNewCode}}
      >Send a new code</Button>
    {{/if}}
  {{/if}}
</template>;

export default CodeErrors;
