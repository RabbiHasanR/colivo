import { module, test } from 'qunit';
import { initials } from 'colivo-web/utils/names';

module('Unit | Utils | names', function () {
  test('initials are the first letters of the first and last name', function (assert) {
    // GIVEN a person's name
    // WHEN  it is shown as an avatar
    // THEN  it reads as one or two capital letters, as on WebHomeEmpty.html
    const cases: Array<[string, string]> = [
      ['Rabbi Hasan', 'RH'],
      ['Maruf', 'M'],
      ['  hijam  ahmed shusil ', 'HS'],
    ];

    for (const [name, shown] of cases) {
      assert.strictEqual(initials(name), shown, name);
    }
  });
});
