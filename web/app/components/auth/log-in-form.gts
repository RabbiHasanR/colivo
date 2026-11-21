import Component from '@glimmer/component';
import { tracked } from '@glimmer/tracking';
import { action } from '@ember/object';
import { on } from '@ember/modifier';
import { service } from '@ember/service';
import type SessionService from '../../services/session';
import Button from '../ui/button';
import Field from '../ui/field';
import Stack from '../ui/stack';
import TextInput from '../ui/text-input';
import CodeField from './code-field';

interface LogInFormSignature {
  Args: { onLoggedIn: () => void };
}

/**
 * "Log in" from colivo-design/web/WebAuth.html: the phone or email the home
 * added you with, then the 6-digit code sent to it (FR-84). No home code.
 */
export default class LogInForm extends Component<LogInFormSignature> {
  @service declare session: SessionService;

  @tracked contact = '';
  @tracked code = '';
  @tracked sentTo: string | null = null;

  @action setContact(value: string): void {
    this.contact = value;
  }

  @action setCode(value: string): void {
    this.code = value;
  }

  @action
  async submit(event: SubmitEvent): Promise<void> {
    event.preventDefault();
    if (this.sentTo === null) {
      await this.session.requestCode(this.contact);
      this.sentTo = this.contact;
      return;
    }
    await this.session.logIn(this.contact, this.code);
    this.args.onLoggedIn();
  }

  <template>
    <form data-test-log-in-form {{on "submit" this.submit}}>
      <Stack>
        <Field @label="Phone or email" data-test-field="contact" as |id|>
          <TextInput
            id={{id}}
            autocomplete="username"
            @value={{this.contact}}
            @onInput={{this.setContact}}
            data-test-log-in-contact
          />
        </Field>
        {{#if this.sentTo}}
          <p data-test-code-sent-to>Sent to {{this.sentTo}}</p>
          <CodeField @value={{this.code}} @onInput={{this.setCode}} />
          <Button type="submit" data-test-log-in-submit>Log in</Button>
        {{else}}
          <Button type="submit" data-test-log-in-send-code>Send code</Button>
        {{/if}}
      </Stack>
    </form>
  </template>
}
