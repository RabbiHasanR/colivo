import { module, test } from 'qunit';
import { firstMonthChoices } from 'colivo-web/utils/months';

module('Unit | Utils | months', function () {
  test('first-month choices are this month and next in the home time zone', function (assert) {
    // GIVEN two moments: mid-November, and 30 Nov 19:00 UTC (already 1 Dec in Dhaka)
    // WHEN  the first-month choices are made for a home in Asia/Dhaka
    // THEN  they are this month and the next, as Dhaka sees them
    const cases: Array<[string, string[]]> = [
      [
        '2026-11-21T10:00:00Z',
        ['2026-11-01 November 2026', '2026-12-01 December 2026'],
      ],
      [
        '2026-11-30T19:00:00Z',
        ['2026-12-01 December 2026', '2027-01-01 January 2027'],
      ],
    ];

    for (const [now, expected] of cases) {
      const choices = firstMonthChoices(new Date(now), 'Asia/Dhaka');

      assert.deepEqual(
        choices.map((choice) => `${choice.value} ${choice.label}`),
        expected,
        now,
      );
    }
  });
});
