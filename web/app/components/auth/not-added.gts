import type { TOC } from '@ember/component/template-only';
import { fn } from '@ember/helper';
import { on } from '@ember/modifier';
import Button from '../ui/button';

interface NotAddedSignature {
  Args: {
    contact: string;
    onCreateHome: (contact: string) => void;
    onTryAnother: () => void;
  };
}

/**
 * "Not added yet" (FR-87, colivo-design/mobile/Login.html): no active home
 * uses this phone or email. Ask the home to add it, or start your own.
 */
const NotAdded: TOC<NotAddedSignature> = <template>
  <section data-test-not-added aria-labelledby="not-added-title">
    <h2 id="not-added-title">Not added yet</h2>
    <p>No home uses {{@contact}} yet.</p>
    <p>If you're joining a shared home, ask its owner or manager to add this
      number. You'll get an SMS or email when it's done.</p>
    <Button
      data-test-create-own-home
      {{on "click" (fn @onCreateHome @contact)}}
    >
      Create my own home
    </Button>
    <Button
      @variant="secondary"
      data-test-try-another
      {{on "click" @onTryAnother}}
    >Try another phone or email</Button>
  </section>
</template>;

export default NotAdded;
