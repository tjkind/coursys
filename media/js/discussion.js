var app;

function set_current_topic(topic) {
    app.current_topic = topic;
    app.$http.get(topic.link, {}).then(response => {
        app.current_replies = response.body;
    }, response => {});
}

function update_topics() {
    app.$http.get(discussion_api_url, {}).then(response => {
        app.topics = response.body;
        if ( response.body.length > 0 ) {
            set_current_topic(response.body[0]); // TODO: actually display the current topic
        }
    }, response => {this.topics = [];});
}

function discussion_setup() {

    Vue.component('discussion-topic-list', {
        props: ['topics'],
        template: '<ul id="discussion-topics"><discussion-topic-listed v-for="topic in topics" v-bind:topic="topic" v-bind:key="topic.slug"></discussion-topic-listed></ul>'
    });

    Vue.component('discussion-topic-listed', {
        props: ['topic'],
        template: '<li>{{ topic.title }}, {{ topic.author }}</li>'
    });

    Vue.component('discussion-topic-main', {
        props: ['topic'],
        template:
            '<section id="main-topic"><h2>{{ topic.title }}</h2>' +
            '<div id="discussion-topic-content" v-html="topic.content_html"' +
            '  v-bind:class="{ tex2jax_process: topic.math, tex2jax_ignore: !topic.math }"></div>' +
            '</section>',
        mounted: function () {
            this.$nextTick(function () {
                if ( this.topic.math ) {
                    MathJax.Hub.Queue(["Typeset", MathJax.Hub, this.$el]);
                }
                highlight_in($(this.$el));
            })
        }
    });

    Vue.component('discussion-topic-replies', {
        props: ['replies'],
        template: '<ul id="discussion-replies" v-if="replies.length > 0">' +
            '<li v-for="reply in replies" v-bind:key="reply.slug">' +
            '  <discussion-reply v-bind:reply="reply"></discussion-reply>' +
            '</li>' +
            '</ul>'
    });

    Vue.component('discussion-reply', {
        props: ['reply'],
        template: '<div class="discussion-reply-content" v-html="reply.content_html"' +
            '  v-bind:class="{ tex2jax_process: reply.math, tex2jax_ignore: !reply.math }"></div>',
        mounted: function () {
            this.$nextTick(function () {
                if ( this.reply.math ) {
                    MathJax.Hub.Queue(["Typeset", MathJax.Hub, this.$el]);
                }
                highlight_in($(this.$el));
            });
        }
    });

    app = new Vue({
        el: '#discussion-container',
        data: {
            topics: [],
            current_topic: null,
            current_replies: [],
        }
    });

    update_topics();
}
$(document).ready(discussion_setup);
