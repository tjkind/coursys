var app;

function create_components() {
    // build the various Vue components that we'll need
    Vue.component('discussion-topic-list', {
        props: ['topics'],
        template: '<ul id="discussion-topics"><discussion-topic-listed v-for="topic in topics" v-bind:topic="topic" v-bind:key="topic.slug"></discussion-topic-listed></ul>'
    });

    Vue.component('discussion-topic-listed', {
        props: ['topic'],
        template: '<li><router-link :to="{ name: \'main_topic\', params: { slug: topic.slug, topic: topic } }">{{ topic.title }}</router-link>, {{ topic.author }}</li>'
    });

    const main_topic = Vue.component('discussion-topic-main', {
        props: ['topic'],
        template:
            '<section id="main-topic"><h2>{{ $route.params }}</h2>' +
            '<div id="discussion-topic-content" v-html="topic.content_html"' +
            '  v-bind:class="{ tex2jax_process: topic.math, tex2jax_ignore: !topic.math }"></div>' +
            '</section>',
        mounted: function () { update_display(this, this.topic.math); },
        updated: function () { update_display(this, this.topic.math); }
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
        mounted: function () { update_display(this, this.reply.math); },
        updated: function () { update_display(this, this.reply.math); }
    });

    const blank = Vue.component('blank', {
        props: [],
        template: '<p>nil</p>'
    });

    const router = new VueRouter({
        //mode: 'history',
        routes: [
            { path: '/', component: blank, name: 'blank' },
            { path: '/:slug', component: main_topic, name: 'main_topic' }
            ]
    });

    return router;
}

function set_current_topic(topic) {
    app.current_topic = topic;
    app.$http.get(topic.link, {}).then(response => {
        app.current_replies = response.body;
    }, response => {});
}

function update_topics() {
    app.$http.get(discussion_api_url, {}).then(response => {
        app.topics = response.body;
        //if ( response.body.length > 0 ) {
        //    set_current_topic(response.body[0]); // TODO: actually display the current topic
        //}
    }, response => {this.topics = [];});
}

function update_display(component, math) {
    component.$nextTick(function () {
        if (math) {
            MathJax.Hub.Queue(["Typeset", MathJax.Hub, component.$el]);
        }
        highlight_in($(component.$el));
    });
}

function discussion_setup() {
    const router = create_components();

    app = new Vue({
        router: router,
        el: '#discussion-container',
        data: {
            topics: [],
            current_topic: null,
            current_replies: [],
        }
    });
    update_topics();
    //router.push('/');
}
$(document).ready(discussion_setup);
