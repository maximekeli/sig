import assert from 'node:assert/strict';
import { describe, it } from 'vitest';
import { buildCommentTree, likeApiPath } from '../js/videos.js';

describe('videos engagement utils', () => {
  it('likeApiPath pour publication et commentaire', () => {
    assert.equal(likeApiPath('post', 5), '/videos/posts/5/toggle_like/');
    assert.equal(likeApiPath('comment', 12), '/videos/comments/12/toggle_like/');
  });

  it('buildCommentTree groupe les réponses sous le parent', () => {
    const flat = [
      { id: 1, parent_id: null, text: 'A' },
      { id: 2, parent_id: 1, text: 'Réponse A' },
      { id: 3, parent_id: null, text: 'B' },
    ];
    const tree = buildCommentTree(flat);
    assert.equal(tree.length, 2);
    assert.equal(tree[0].id, 1);
    assert.equal(tree[0].replies.length, 1);
    assert.equal(tree[0].replies[0].text, 'Réponse A');
    assert.equal(tree[1].id, 3);
    assert.equal(tree[1].replies.length, 0);
  });
});
