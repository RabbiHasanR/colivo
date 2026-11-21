import Component from '@glimmer/component';
import { tracked } from '@glimmer/tracking';
import { registerDestructor } from '@ember/destroyable';
import type Owner from '@ember/owner';
import { formatCountdown } from '../../utils/countdown';

interface CountdownSignature {
  Element: HTMLSpanElement;
  /** `@seconds` null (unknown) shows 0:00. */
  Args: { seconds: number | null; onDone?: () => void };
}

const TICK_MS = 1000;

/**
 * Seconds left, shown as `14:52` and counting down once a second; calls
 * `@onDone` at 0:00. The timer stops when the countdown leaves the page.
 */
export default class Countdown extends Component<CountdownSignature> {
  /** Whole seconds since the countdown appeared. */
  @tracked elapsed = 0;

  get left(): number {
    return (this.args.seconds ?? 0) - this.elapsed;
  }

  constructor(owner: Owner, args: CountdownSignature['Args']) {
    super(owner, args);
    if (this.left <= 0) return;
    const timer = setInterval(() => {
      this.elapsed += 1;
      if (this.left <= 0) {
        clearInterval(timer);
        this.args.onDone?.();
      }
    }, TICK_MS);
    registerDestructor(this, () => clearInterval(timer));
  }

  <template>
    <span ...attributes>{{formatCountdown this.left}}</span>
  </template>
}
