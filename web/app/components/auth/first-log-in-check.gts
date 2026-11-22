import Component from '@glimmer/component';
import { tracked } from '@glimmer/tracking';
import { action } from '@ember/object';
import { get } from '@ember/helper';
import { on } from '@ember/modifier';
import { service } from '@ember/service';
import type SessionService from '../../services/session';
import type { Me } from '../../services/session';
import { formatDate } from '../../utils/dates';
import { refusalFrom, type Refusal } from '../../utils/refusal';
import { roleLabel } from '../../utils/roles';
import Button from '../ui/button';
import Card from '../ui/card';
import Field from '../ui/field';
import FormError from '../ui/form-error';
import Stack from '../ui/stack';
import TextInput from '../ui/text-input';

interface FirstLogInCheckSignature {
  Args: { me: Me; onChecked: () => void };
}

/**
 * A member's first log-in (FR-86, colivo-design/mobile/Login.html): the
 * home, role and join date to check, and their name to fix. The join date
 * is changed only by the owner or a manager.
 */
export default class FirstLogInCheck extends Component<FirstLogInCheckSignature> {
  @service declare session: SessionService;

  @tracked typedName: string | null = null;
  @tracked refusal: Refusal | null = null;

  get name(): string {
    return this.typedName ?? this.args.me.membership.name;
  }

  get fieldErrors(): Record<string, string[]> {
    return this.refusal?.fieldErrors ?? {};
  }

  @action setName(value: string): void {
    this.typedName = value;
  }

  @action
  async submit(event: SubmitEvent): Promise<void> {
    event.preventDefault();
    this.refusal = null;
    try {
      await this.session.updateMe(this.name);
    } catch (error) {
      this.refusal = refusalFrom(error);
      if (!this.refusal) throw error;
      return;
    }
    this.args.onChecked();
  }

  <template>
    <section
      class="mx-auto flex w-full max-w-[440px] flex-col gap-4"
      data-test-first-log-in-check
      aria-labelledby="first-log-in-title"
    >
      <h1 id="first-log-in-title" class="text-[28px] font-semibold">Welcome,
        check your details once</h1>
      <Card class="flex flex-col gap-1 p-5">
        <p class="text-xs text-muted">You were added to</p>
        <p class="font-display text-xl font-semibold">{{@me.home.name}}</p>
        <p class="text-sm">{{roleLabel @me.membership.role}}
          {{#if @me.membership.joined_on}}
            · From
            {{formatDate @me.membership.joined_on}}
          {{/if}}</p>
        {{#if @me.membership.added_by_name}}
          <p class="text-[13px] text-muted">Added by
            {{@me.membership.added_by_name}}</p>
        {{/if}}
      </Card>
      <form
        class="rounded-card border border-line bg-surface p-5"
        {{on "submit" this.submit}}
      >
        <Stack>
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
              data-test-first-log-in-name
            />
          </Field>
          {{#if this.refusal.message}}
            <FormError>{{this.refusal.message}}</FormError>
          {{/if}}
          <p class="text-[13px] leading-normal text-muted">Something wrong, like
            the join date? Ask your home's owner or a manager: only they can
            change it.</p>
          <Button type="submit" @size="lg" data-test-go-to-my-home>Go to my home</Button>
        </Stack>
      </form>
    </section>
  </template>
}
