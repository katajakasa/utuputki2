'use strict';

app.factory('Player', ['$location', '$rootScope', 'SockService', 'Playlist', 'AUTH_EVENTS', 'SYNC_EVENTS',
    function ($location, $rootScope, SockService, Playlist, AUTH_EVENTS, SYNC_EVENTS) {
        var last_error = "";
        var players = [];
        var current_player = null;
        var req_skip_count = 1;
        var media_skip_count = 0;

        function player_event(msg, query) {
            if (msg['error'] == 1) {
                last_error = msg['data']['message'];
            } else {
                if(query == 'fetchall') {
                    players = msg['data'];
                    $rootScope.$broadcast(SYNC_EVENTS.playersRefresh);
                    if(current_player == null && players.length > 0) {
                        current_player = players[0];
                        $rootScope.$broadcast(SYNC_EVENTS.currentPlayerChange);
                    }
                    return;
                }
                if(query == 'change') {
                    for(var i = 0; i < players.length; i++) {
                        if(players[i].id == msg['data']['state']['id']) {
                            players[i] = msg['data']['state'];
                            if(current_player != null && current_player.id == players[i].id) {
                                current_player = players[i];
                            }
                        }
                    }
                    $rootScope.$broadcast(SYNC_EVENTS.playerPlaybackChange);
                    return;
                }
                if(query == 'req_skip_count') {
                    req_skip_count = msg['data']['count'];
                    $rootScope.$broadcast(SYNC_EVENTS.playerSkipCountChange);
                    return;
                }
                if(query == 'current_skip_count') {
                    media_skip_count = msg['data']['count'];
                    $rootScope.$broadcast(SYNC_EVENTS.playerSkipCountChange);
                    return;
                }
                console.error("Unidentified query type.");
            }
        }

        function setup() {
            SockService.add_recv_handler('player', player_event);
            $rootScope.$on(AUTH_EVENTS.loginSuccess, function (event, args) {
                SockService.send_msg('player', {}, 'fetchall');
                SockService.send_msg('player', {}, 'req_skip_count');
                var c_player = get_current_player();
                if(c_player != null) {
                    SockService.send_msg('player', {'player_id': c_player.id}, 'now_playing');
                    SockService.send_msg('player', {'player_id': c_player.id}, 'get_media_skip_count');
                }
            });
        }

        function get_players(event_id) {
            var out = [];
            for(var i = 0; i < players.length; i++) {
                if(players[i].event_id == event_id) {
                    out.push(players[i]);
                }
            }
            return out;
        }

        function get_current_player() {
            return current_player;
        }

        function get_current_media() {
            var c_player = get_current_player();
            if(c_player != null) {
                return Playlist.get_media(c_player.last);
            }
            return null;
        }

        function get_current_status() {
            var c_player = get_current_player();
            if(c_player != null) {
                return c_player.status;
            }
            return 0;
        }

        function skip_current() {
            var c_player = get_current_player();
            if(c_player != null) {
                SockService.send_msg('player', {'player_id': c_player.id}, 'skip');
            }
        }

        function set_current_player(player) {
            current_player = player;
            $rootScope.$broadcast(SYNC_EVENTS.currentPlayerChange);
        }

        function get_req_skip_count() {
            return req_skip_count;
        }

        function get_current_skip_count() {
            return media_skip_count;
        }

        function get_last_error() {
            return last_error;
        }

        function refresh() {
            SockService.send_msg('player', {}, 'req_skip_count');
            var c_player = get_current_player();
            if(c_player != null) {
                SockService.send_msg('player', {'player_id': c_player.id}, 'now_playing');
                SockService.send_msg('player', {'player_id': c_player.id}, 'get_media_skip_count');
            }
        }

        return {
            setup: setup,
            get_players: get_players,
            get_last_error: get_last_error,
            get_current_player: get_current_player,
            set_current_player: set_current_player,
            get_req_skip_count: get_req_skip_count,
            get_current_media: get_current_media,
            get_current_status: get_current_status,
            get_current_skip_count: get_current_skip_count,
            skip_current: skip_current,
            refresh: refresh
        };
    }
]);
