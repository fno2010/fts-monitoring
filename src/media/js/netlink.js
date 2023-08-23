function NetlinkCtrl($rootScope, $location, $scope, netlink, Netlink)
{
    $scope.netlink = netlink;

    // Filter
    $scope.showFilterDialog = function() {
        document.getElementById('filterDialog').style.display = 'block';
    }

    $scope.cancelFilters = function() {
        document.getElementById('filterDialog').style.display = 'none';
    }

    $scope.filter = {
        limit: parseInt($location.$$search.limit)
    }

    $scope.applyFilters = function() {
        $location.search($scope.filter);
        document.getElementById('filterDialog').style.display = 'none';
    }

    // On page change, reload
    $scope.pageChanged = function(newPage) {
        $location.search('page', newPage);
    };

    // Set timer to trigger autorefresh
    $scope.autoRefresh = setInterval(function() {
        loading($rootScope);
        var filter = $location.$$search;
        filter.page = $scope.netlink.page;
        Netlink.query(filter, function(updatedNetlink) {
            $scope.netlink = updatedNetlink;
            stopLoading($rootScope);
        },
        genericFailureMethod(null, $rootScope, $location));
    }, REFRESH_INTERVAL);
    $scope.$on('$destroy', function() {
        clearInterval($scope.autoRefresh);
    });
}


NetlinkCtrl.resolve = {
    netlink: function ($rootScope, $location, $route, $q, Netlink) {
        loading($rootScope);

        var deferred = $q.defer();

        Netlink.query($location.$$search,
              genericSuccessMethod(deferred, $rootScope),
              genericFailureMethod(deferred, $rootScope, $location));

        return deferred.promise;
    }
}


function NetlinkTracesCtrl($rootScope, $location, $scope, traces, NetlinkTraces)
{
    $scope.traces = traces;

    // Filter
    $scope.showFilterDialog = function() {
        document.getElementById('filterDialog').style.display = 'block';
    }

    $scope.cancelFilters = function() {
        document.getElementById('filterDialog').style.display = 'none';
    }

    $scope.filter = {
        limit: parseInt($location.$$search.limit)
    }

    $scope.applyFilters = function() {
        $location.search($scope.filter);
        document.getElementById('filterDialog').style.display = 'none';
    }

    // On page change, reload
    $scope.pageChanged = function(newPage) {
        $location.search('page', newPage);
    };

    // Set timer to trigger autorefresh
    $scope.autoRefresh = setInterval(function() {
        loading($rootScope);
        var filter = $location.$$search;
        filter.page = $scope.netlink.page;
        Netlink.query(filter, function(updatedNetlink) {
            $scope.netlink = updatedNetlink;
            stopLoading($rootScope);
        },
        genericFailureMethod(null, $rootScope, $location));
    }, REFRESH_INTERVAL);
    $scope.$on('$destroy', function() {
        clearInterval($scope.autoRefresh);
    });
}


NetlinkTracesCtrl.resolve = {
    traces: function ($rootScope, $location, $route, $q, NetlinkTraces) {
        loading($rootScope);

        var deferred = $q.defer();

        NetlinkTraces.query($location.$$search,
              genericSuccessMethod(deferred, $rootScope),
              genericFailureMethod(deferred, $rootScope, $location));

        return deferred.promise;
    }
}


function NetlinkDetailedCtrl($rootScope, $location, $scope, netlink, NetlinkDetailed, Unique)
{
    $scope.unique = {
        activities: Unique.query({field:'activities'}),
        hostnames: Unique.query({field:'hostnames'}),
    }

    $scope.netlink = netlink

    // Queue entries
    $scope.transfers = netlink.transfers;

    // On page change, reload
    $scope.pageChanged = function(newPage) {
        $location.search('page', newPage);
    };

    // Set timer to trigger autorefresh
    $scope.autoRefresh = setInterval(function() {
        loading($rootScope);
        var filter = $location.$$search;
        filter.page = $scope.transfers.page;
        Transfers.query(filter, function(updatedTransfers) {
            $scope.transfers = updatedTransfers;
            stopLoading($rootScope);
        },
        genericFailureMethod(null, $rootScope, $location));
    }, REFRESH_INTERVAL);
    $scope.$on('$destroy', function() {
        clearInterval($scope.autoRefresh);
    });

    // Set up filters
    $scope.filter = {
        vo:          validString($location.$$search.vo),
        source_se:   validString($location.$$search.source_se),
        dest_se:     validString($location.$$search.dest_se),
        source_surl: validString($location.$$search.source_surl),
        dest_surl:   validString($location.$$search.dest_surl),
        time_window: parseInt(validString($location.$$search.time_window)),
        state:       statesFromString($location.$$search.state),
        activity:    validString($location.$$search.activity),
        hostname:    validString($location.$$search.hostname),
    }

    $scope.showFilterDialog = function() {
        document.getElementById('filterDialog').style.display = 'block';
    }

    $scope.cancelFilters = function() {
        document.getElementById('filterDialog').style.display = 'none';
    }

    $scope.applyFilters = function() {
        $location.search({
            page:         1,
            source_surl:  $scope.filter.source_surl,
            dest_surl:    $scope.filter.dest_surl,
            time_window:  $scope.filter.time_window,
            state:        joinStates($scope.filter.state),
            activity:     validString($scope.filter.activity),
            hostname:     validString($scope.filter.hostname),
        });
        document.getElementById('filterDialog').style.display = 'none';
    }
}


NetlinkDetailedCtrl.resolve = {
    netlink: function($rootScope, $location, $q, NetlinkDetailed) {
        loading($rootScope);

        var deferred = $q.defer();

        var page = $location.$$search.page;
        if (!page || page < 1)
            page = 1;

        NetlinkDetailed.query($location.$$search,
                        genericSuccessMethod(deferred, $rootScope),
                        genericFailureMethod(deferred, $rootScope, $location));

        return deferred.promise;
    }
}
