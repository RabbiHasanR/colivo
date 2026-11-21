import Component from '@glimmer/component';
import { tracked } from '@glimmer/tracking';
import { action } from '@ember/object';
import { on } from '@ember/modifier';
import { service } from '@ember/service';
import type SessionService from '../../services/session';
import { codeErrorFrom, type CodeError } from '../../utils/code-error';
import Button from '../ui/button';
import Field from '../ui/field';
import Stack from '../ui/stack';
import TextInput from '../ui/text-input';
import CodeErrors from './code-errors';
import CodeField from './code-field';
import Countdown from '../ui/countdown';

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
  @tracked codeError: CodeError | null = null;
  /** Seconds until a new code may be sent, from the API's last answer. */
  @tracked resendIn = 0;
  @tracked canResend = false;
  /** Shown after "Resend": where the new code went. */
  @tracked resentTo: string | null = null;

  @action setContact(value: string): void {
    this.contact = value;
  }

  @action setCode(value: string): void {
    this.code = value;
  }

  @action
  async submit(event: SubmitEvent): Promise<void> {
    event.preventDefault();
    await this.refusable(() =>
      this.sentTo === null ? this.sendCode() : this.logIn(),
    );
  }

  @action
  async sendNewCode(): Promise<void> {
    await this.refusable(() => this.sendCode());
  }

  @action
  useDifferentContact(): void {
    this.sentTo = null;
    this.contact = '';
    this.code = '';
    this.codeError = null;
  }

  @action
  async resend(): Promise<void> {
    await this.refusable(async () => {
      await this.sendCode();
      this.resentTo = this.contact;
    });
  }

  @action
  allowResend(): void {
    this.canResend = true;
  }

  async sendCode(): Promise<void> {
    const sent = await this.session.requestCode(this.contact);
    this.sentTo = this.contact;
    this.code = '';
    this.resentTo = null;
    this.resendIn = sent.resend_in_seconds;
    this.canResend = sent.resend_in_seconds <= 0;
  }

  async logIn(): Promise<void> {
    await this.session.logIn(this.contact, this.code);
    this.args.onLoggedIn();
  }

  /** Run a step; a refused code shows why instead of failing the page. */
  async refusable(step: () => Promise<void>): Promise<void> {
    this.codeError = null;
    try {
      await step();
    } catch (error) {
      this.codeError = codeErrorFrom(error);
      if (!this.codeError) throw error;
    }
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
        {{#if this.codeError}}
          <CodeErrors
            @error={{this.codeError}}
            @onSendNewCode={{this.sendNewCode}}
            @onUseDifferentContact={{this.useDifferentContact}}
          />
        {{/if}}
        {{#if this.sentTo}}
          <p data-test-code-sent-to>Sent to {{this.sentTo}}</p>
          <CodeField @value={{this.code}} @onInput={{this.setCode}} />
          {{#if this.resentTo}}
            <p data-test-code-resent>New code sent to
              {{this.resentTo}}. The old one no longer works.</p>
          {{/if}}
          <Button type="submit" data-test-log-in-submit>Log in</Button>
          {{#if this.canResend}}
            <Button
              @variant="secondary"
              data-test-resend
              {{on "click" this.resend}}
            >Resend</Button>
          {{else}}
            <p data-test-resend-wait>Didn't get it? Resend in
              <Countdown
                @seconds={{this.resendIn}}
                @onDone={{this.allowResend}}
              /></p>
          {{/if}}
        {{else}}
          <Button type="submit" data-test-log-in-send-code>Send code</Button>
        {{/if}}
      </Stack>
    </form>
  </template>
}
