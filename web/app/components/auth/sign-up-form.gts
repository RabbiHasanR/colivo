import Component from '@glimmer/component';
import { tracked } from '@glimmer/tracking';
import { action } from '@ember/object';
import { get } from '@ember/helper';
import { on } from '@ember/modifier';
import { service } from '@ember/service';
import type SessionService from '../../services/session';
import { ApiError } from '../../utils/api-error';
import { DEFAULT_TIME_ZONE, firstMonthChoices } from '../../utils/months';
import Button from '../ui/button';
import Checkbox from '../ui/checkbox';
import Field from '../ui/field';
import FormError from '../ui/form-error';
import Select from '../ui/select';
import Stack from '../ui/stack';
import TextInput from '../ui/text-input';
import CodeField from './code-field';

interface SignUpFormSignature {
  Args: {
    /** The current time; tests fix it. */
    now?: Date;
    /** A phone or email to start with ("Not added yet" → "Create my own home"). */
    contact?: string | null;
    onSignedUp: () => void;
  };
}

/**
 * "Create your home" from colivo-design/web/WebAuth.html: who you are and
 * your home, then the 6-digit code sent to your phone or email (FR-83).
 */
export default class SignUpForm extends Component<SignUpFormSignature> {
  @service declare session: SessionService;

  readonly monthChoices = firstMonthChoices(
    this.args.now ?? new Date(),
    DEFAULT_TIME_ZONE,
  );

  @tracked name = '';
  /** What the person typed; until then, `@contact`. */
  @tracked typedContact: string | null = null;

  get contact(): string {
    return this.typedContact ?? this.args.contact ?? '';
  }
  @tracked homeName = '';
  @tracked area = '';
  @tracked firstMonth = this.monthChoices[0]?.value ?? '';
  @tracked livesHere = true;
  @tracked code = '';
  @tracked sentTo: string | null = null;
  /** The API's 422 messages, by field name (`name`, `home_name` …). */
  @tracked fieldErrors: Record<string, string[]> = {};
  /** Why the API refused the sign-up, when it isn't about one field. */
  @tracked error: string | null = null;

  @action setName(value: string): void {
    this.name = value;
  }

  @action setContact(value: string): void {
    this.typedContact = value;
  }

  @action setHomeName(value: string): void {
    this.homeName = value;
  }

  @action setArea(value: string): void {
    this.area = value;
  }

  @action setFirstMonth(value: string): void {
    this.firstMonth = value;
  }

  @action setLivesHere(value: boolean): void {
    this.livesHere = value;
  }

  @action setCode(value: string): void {
    this.code = value;
  }

  @action
  async submit(event: SubmitEvent): Promise<void> {
    event.preventDefault();
    this.fieldErrors = {};
    this.error = null;
    try {
      if (this.sentTo === null) {
        await this.sendCode();
      } else {
        await this.createHome();
      }
    } catch (error) {
      if (!this.showRefusal(error)) throw error;
    }
  }

  async sendCode(): Promise<void> {
    await this.session.requestCode(this.contact);
    this.sentTo = this.contact;
  }

  async createHome(): Promise<void> {
    await this.session.signUp({
      contact: this.contact,
      code: this.code,
      name: this.name,
      home_name: this.homeName,
      area: this.area.trim() || null,
      first_month: this.firstMonth,
      lives_here: this.livesHere,
    });
    this.args.onSignedUp();
  }

  /**
   * Show why the API refused: 422 messages under their fields, anything else
   * above the button. Returns false for errors that aren't a refusal.
   */
  showRefusal(error: unknown): boolean {
    if (!(error instanceof ApiError) || error.status === null) return false;
    if (error.kind === 'validation') {
      this.fieldErrors = error.fieldErrors;
    } else {
      this.error = error.message;
    }
    return true;
  }

  <template>
    <form
      class="rounded-card border border-line bg-surface p-5"
      data-test-sign-up-form
      {{on "submit" this.submit}}
    >
      <Stack>
        <div class="grid grid-cols-[repeat(auto-fit,minmax(170px,1fr))] gap-3">
          <Field
            @label="Your name"
            @errors={{get this.fieldErrors "name"}}
            data-test-field="name"
            as |id|
          >
            <TextInput
              id={{id}}
              autocomplete="name"
              @value={{this.name}}
              @onInput={{this.setName}}
              data-test-sign-up-name
            />
          </Field>
          <Field
            @label="Phone or email"
            @errors={{get this.fieldErrors "contact"}}
            data-test-field="contact"
            as |id|
          >
            <TextInput
              id={{id}}
              autocomplete="username"
              @value={{this.contact}}
              @onInput={{this.setContact}}
              data-test-sign-up-contact
            />
          </Field>
          <Field
            @label="Home name"
            @errors={{get this.fieldErrors "home_name"}}
            data-test-field="home_name"
            as |id|
          >
            <TextInput
              id={{id}}
              @value={{this.homeName}}
              @onInput={{this.setHomeName}}
              data-test-sign-up-home-name
            />
          </Field>
          <Field
            @label="Area (optional)"
            @errors={{get this.fieldErrors "area"}}
            data-test-field="area"
            as |id|
          >
            <TextInput
              id={{id}}
              @value={{this.area}}
              @onInput={{this.setArea}}
              data-test-sign-up-area
            />
          </Field>
          <Field
            @label="First month"
            @errors={{get this.fieldErrors "first_month"}}
            data-test-field="first_month"
            as |id|
          >
            <Select
              id={{id}}
              @options={{this.monthChoices}}
              @value={{this.firstMonth}}
              @onChange={{this.setFirstMonth}}
              data-test-sign-up-first-month
            />
          </Field>
        </div>
        <Checkbox
          @checked={{this.livesHere}}
          @onChange={{this.setLivesHere}}
          data-test-sign-up-lives-here
        >
          I live here too and pay my share
        </Checkbox>

        {{#if this.error}}
          <FormError data-test-sign-up-error>{{this.error}}</FormError>
        {{/if}}

        {{#if this.sentTo}}
          <p class="text-sm text-muted" data-test-code-sent-to>Sent to
            {{this.sentTo}}</p>
          <CodeField
            @value={{this.code}}
            @onInput={{this.setCode}}
            @errors={{get this.fieldErrors "code"}}
          />
          <Button type="submit" @size="lg" data-test-sign-up-submit>Create home</Button>
        {{else}}
          <Button type="submit" @size="lg" data-test-sign-up-send-code>Send code</Button>
        {{/if}}
      </Stack>
    </form>
  </template>
}
