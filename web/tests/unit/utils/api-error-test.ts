import { module, test } from 'qunit';
import { ApiError, refusalReason } from 'colivo-web/utils/api-error';

module('Unit | Utils | api-error', function () {
  const cases: [string, unknown, string | null][] = [
    [
      'a 409 asking to choose a home',
      new ApiError(
        'Choose a home.',
        409,
        'conflict',
        {},
        { reason: 'choose_home' },
      ),
      'choose_home',
    ],
    [
      'a 403 for a home they left',
      new ApiError(
        'No longer a member.',
        403,
        'forbidden',
        {},
        { reason: 'not_in_home' },
      ),
      'not_in_home',
    ],
    [
      'a 403 for their role',
      new ApiError("Your role can't do this.", 403, 'forbidden'),
      null,
    ],
    [
      'a wrong code',
      new ApiError(
        "That code isn't right.",
        400,
        'rule',
        {},
        { reason: 'wrong' },
      ),
      null,
    ],
    ['an error that is not from the API', new Error('boom'), null],
  ];
  for (const [name, error, expected] of cases) {
    test(`refusalReason reads why a home was refused: ${name}`, function (assert) {
      // GIVEN an error from a request
      // WHEN  asking whether it refused the home the request named
      // THEN  it is choose_home or not_in_home for those refusals, else null
      assert.strictEqual(refusalReason(error), expected);
    });
  }
});
