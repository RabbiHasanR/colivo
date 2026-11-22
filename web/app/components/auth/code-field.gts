import type { TOC } from '@ember/component/template-only';
import Field from '../ui/field';
import TextInput from '../ui/text-input';

interface CodeFieldSignature {
  Args: {
    value: string;
    onInput: (value: string) => void;
    errors?: string[];
  };
}

/**
 * The 6-digit one-time code. Phones show the number pad and offer the code
 * from the SMS (`autocomplete="one-time-code"`).
 */
const CodeField: TOC<CodeFieldSignature> = <template>
  <Field @label="6-digit code" @errors={{@errors}} as |id|>
    <TextInput
      id={{id}}
      inputmode="numeric"
      autocomplete="one-time-code"
      maxlength="6"
      placeholder="••••••"
      @code={{true}}
      @value={{@value}}
      @onInput={{@onInput}}
      data-test-code-field
    />
  </Field>
</template>;

export default CodeField;
