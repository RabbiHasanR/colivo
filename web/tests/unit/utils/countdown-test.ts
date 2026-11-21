import { module, test } from 'qunit';
import { formatCountdown } from 'colivo-web/utils/countdown';

module('Unit | Utils | countdown', function () {
  test('formats seconds left as minutes and seconds', function (assert) {
    // GIVEN some seconds left to wait
    // WHEN  they are shown as a countdown
    // THEN  they read as m:ss, as on WebAuthErrors.html
    const cases: Array<[number, string]> = [
      [892, '14:52'],
      [45, '0:45'],
      [0, '0:00'],
      [-3, '0:00'],
    ];

    for (const [seconds, shown] of cases) {
      assert.strictEqual(formatCountdown(seconds), shown, `${seconds} s`);
    }
  });
});
