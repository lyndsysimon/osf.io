/*global describe, it, expect, example, before, after, beforeEach, afterEach, mocha, sinon*/
'use strict';
var assert = require('chai').assert;
var $ = require('jquery');
var faker = require('faker');

window.contextVars.currentUser = {
    name: faker.name.findName(),
    id: 1
};
var registrationUtils = require('js/registrationUtils');

var utilities = registrationUtils.utilities;
var Comment = registrationUtils.Comment;
var Question = registrationUtils.Question;
var MetaSchema = registrationUtils.MetaSchema;
var Draft = registrationUtils.Draft;
var RegistrationEditor = registrationUtils.RegistrationEditor;
var RegistrationManager = registrationUtils.RegistrationManager;

var mkMetaSchema = function() {
    var questions = {};
    var qid;
    [1, 1, 1].map(function() {
        qid = faker.internet.ip();
        questions[qid] = {
            type: 'string',
            format: 'text'
        };
    });

    var params = {
        schema_name: 'My Schema',
        schema_version: 1,
        title: 'A schema',
        schema: {
            title: 'A schema',
            version: 1,
            description: 'A very interesting schema',
            fulfills: [],
            pages: [1, 1, 1].map(function() {
                return {
                    id: faker.internet.ip(),
                    title: 'Page',
                    questions: questions
                };
            })
        },
        id: 'asdfg'
    };

    var ms = new MetaSchema(params);
    return [qid, params, ms];
};


describe('Utilites', () => {
    describe('not', () => {
        it('returns a partial function that negates the return value of callables', () => {
            var I = function(cond){
                return !!cond;
            };
            var notI = utilities.not(I);
            assert.isTrue(notI(false));
            assert.isFalse(notI(true));
        });
        it('returns a partial function that negates the value of non callables', () => {
            assert.isTrue(utilities.not(false)());
            assert.isFalse(utilities.not(true)());
        });
    });
    describe('validators', () => {
        describe('#string', () => {
            it('is valid if the string is not blank', () => {
                assert.isTrue(utilities.validators.string('abc'));
                assert.isFalse(utilities.validators.string(''));
                assert.isFalse(utilities.validators.string('    '));
            });
        });
        describe('#number', () => {
            it('is valid if the value is not blank and is either a number or a string that can be parsed as a number', () => {
                assert.isTrue(utilities.validators.number('1'));
                assert.isTrue(utilities.validators.number(42));
                assert.isFalse(utilities.validators.number('abc'));
                assert.isFalse(utilities.validators.number(false));
            });
        });
    });
});

describe('Comment', () => {
    describe('#constructor', () => {
        it('loads in optional instantiation data', () => {
            var user = {
                name: faker.name.findName(),
                id: 2
            };
            var data = {
                user: user,
                lastModified: faker.date.past(),
                value: faker.lorem.sentence()
            };
            var comment = new Comment(data);
            assert.equal(comment.user, user);
            assert.equal(comment.lastModified.toString(), new Date(data.lastModified).toString());
            assert.equal(comment.value(), data.value);
        });
        it('defaults user to the global currentUser', () => {
            var comment = new Comment();
            assert.deepEqual(comment.user, window.contextVars.currentUser);
        });
    });
    describe('#canDelete', () => {
        it('is true if the global currentUser is the same as comment.user', () => {
            var comment = new Comment();
            assert.isTrue(comment.canDelete());

            var user = {
                name: faker.name.findName(),
                id: 2
            };
            var data = {
                user: user,
                lastModified: faker.date.past(),
                value: faker.lorem.sentence()
            };
            comment = new Comment(data);
            assert.isFalse(comment.canDelete());
        });
    });
    describe('#canEdit', () => {
        it('is true if the comment is saved and the current user is the comment creator', () => {
            var comment = new Comment();
            assert.isFalse(comment.canEdit());
            comment.saved(true);
            assert.isTrue(comment.canEdit());

            var user = {
                name: faker.name.findName(),
                id: 2
            };
            var data = {
                user: user,
                lastModified: faker.date.past(),
                value: faker.lorem.sentence()
            };
            comment = new Comment(data);
            assert.isFalse(comment.canEdit());
            comment.saved(true);
            assert.isFalse(comment.canEdit());
        });
    });
});

describe('Question', () => {
    var id, question, q;
    beforeEach(() => {
        id = faker.internet.ip();
        question = {
            title: faker.internet.domainWord(),
            nav: faker.internet.domainWord(),
            type: 'string',
            format: 'text',
            description: faker.lorem.sentence(),
            help: faker.lorem.sentence(),
            options: [1, 1, 1].map(faker.internet.domainWord)
        };
        q = new Question(question, id);
    });

    describe('#constructor', () => {
        it('loads in optional instantiation data', () => {
            assert.equal(q.id, id);
            assert.equal(q.title, question.title);
            assert.equal(q.nav, question.nav);
            assert.equal(q.type, question.type);
            assert.equal(q.format, question.format);
            assert.equal(q.description, question.description);
            assert.equal(q.help, question.help);
            assert.equal(q.options, question.options);
            assert.isDefined(q.value);
        });
    });
    describe('#allowAddNext', () => {
        it('is true if the Question\'s nextComment is not blank', () => {
            assert.isFalse(q.allowAddNext());
            q.nextComment('not blank');
            assert.isTrue(q.allowAddNext());
        });
    });
    describe('#isComplete', () => {
        it('is true if the Question\'s value is not blank', () => {
            assert.isFalse(q.isComplete());
            q.value('not blank');
            assert.isTrue(q.isComplete());
        });
    });
    describe('#valid', () => {
        it('is true if the Question\'s value passes the corresponding validator\'s checks', () => {
            // q is string type
            assert.isFalse(q.valid());
            q.value('not blank');
            assert.isTrue(q.valid());
        });
    });
    describe('#init', () => {
        it('maps object-type Question\'s properties property to sub-Questions', () => {
            var props = {
                foo: {
                    type: 'number'
                }
            };

            var objType = new Question({
                type: 'object',
                properties: props
            });
            var obj = new Question(objType);
            assert.equal(obj.properties.foo.id, 'foo');
            assert.isDefined(obj.properties.foo.value);
        });
    });
    describe('#addComment', () => {
        it('creates a new Comment using the value of Question.nextComment, and clears Question.nextComment', () => {
            assert.equal(q.comments().length, 0);
            q.nextComment('A good comment');
            q.addComment();
            assert.equal(q.comments().length, 1);
            assert.equal(q.nextComment(), '');
        });
    });
    describe('#toggleExample', () => {
        it('toggles the value of Question.showExample', () => {
            assert.isFalse(q.showExample());
            q.toggleExample();
            assert.isTrue(q.showExample());
        });
    });
});

describe('MetaSchema', () => {
    describe('#constructor', () => {
        it('loads optional instantion data and maps question data to Question instances', () => {

            var ctx = mkMetaSchema();
            var qid = ctx[0];
            var params = ctx[1];
            var ms = ctx[2];
            assert.equal(ms.name, params.schema_name);
            assert.equal(ms.version, params.schema_version);
            assert.equal(ms.schema.pages[0].id, params.schema.pages[0].id);

            assert.isDefined(ms.schema.pages[2].questions[qid].value);
        });
    });
    describe('#flatQuestions', () => {
        it('creates a flat array of the schema questions', () => {
            var ctx = mkMetaSchema();
            var qid = ctx[0];
            var params = ctx[1];
            var ms = ctx[2];

            var questions = [];
            $.each(params.schema.pages, function(i, page) {
                $.each(page.questions, function(qid, question) {
                    questions.push(question);
                });
            });
            assert.deepEqual(questions, ms.flatQuestions());
        });
    });
});

describe('Draft', () => {
    describe('#constructor', () => {
        it('loads optional instantiation data and metaSchema instance', () => {
            var ms = mkMetaSchema()[2];

            var params = {
                pk: faker.random.number(),
                registration_metadata: {},
                initiator: {
                    name: faker.name.findName(),
                    id: faker.internet.ip()
                },
                initiated: faker.date.past(),
                updated: faker.date.past()
            };

            var draft = new Draft(params, ms);

            assert.equal(draft.metaSchema.name, ms.name);
            assert.equal(draft.initiator.id, params.initiator.id);
            assert.equal(draft.updated.toString(), params.updated.toString());
        });
        it('calculates a percent completion based on the passed registration_metadata', () => {
            var ms = mkMetaSchema()[2];

            var data = {};
            var questions = ms.flatQuestions();
            $.each(questions, function(i, q) {
                data[q.id] = {
                    value: 'value'
                };
            });

            var params = {
                pk: faker.random.number(),
                registration_metadata: data,
                initiator: {
                    name: faker.name.findName(),
                    id: faker.internet.ip()
                },
                initiated: faker.date.past(),
                updated: faker.date.past()
            };

            var draft = new Draft(params, ms);

            assert.equal(draft.completion(), 100);
        });
    });
});

describe('RegistrationEditor', () => {

});